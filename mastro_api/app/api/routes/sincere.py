#!/usr/bin/env python3
import os
import time
from datetime import datetime, timedelta
from math import ceil
from typing import Any
from uuid import UUID

import pandas as pd
from fastapi import (
    APIRouter,
    HTTPException,
    Query,
    Request,
    Response,
    status,
)
from fastapi.responses import FileResponse
from sqlalchemy import exc, func, text
from sqlmodel import Session, select

from app.api.deps import CurrentUser, SessionDep, get_engine_if_register
from app.core.config import settings
from app.models import (
    Channel,
    Device,
    MetaData,
)
from app.responses import (
    DataPagination,
    DevicePagination,
    DevicesListWithChannels,
    DeviceWithChannelsNoPagination,
    SimpleListResponse,
)

router = APIRouter()

BASE_DIR = settings.BASE_DIR
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'temp')


@router.get("/databases", response_model=list[str])
def get_databases(session: SessionDep) -> Any:
    databases_evn = settings.PGSQL_DATA_VALUE_DATABASES
    return databases_evn.split(",")


@router.get("/{database}/", response_model=list[Device])
def read_items(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:

    if current_user.is_superuser:
        statement = select(Device).offset(skip).limit(limit)
        return session.exec(statement).all()
    else:
        statement = (
            select(Device)
            .where(Device.owner_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )
        return session.exec(statement).all()


# @router.get("/model_data/{measurement}/{channel_id}", response_model= Any)
# def model_data(
#     session: SessionDep,
#     measurement: str,
#     channel_id: UUID, skip: int = 0, limit: int = 100
# ) -> Any:
#     statement = (
#         select(MetaData)
#     )
#     return session.exec(statement).all()


@router.get("/{database}/meta_data/{measurement}/{channel_id}", response_model= Any)
def get_meta_data(
    session: SessionDep,
    database: str,
    measurement: str,
    channel_id: UUID,
    datetime_from: datetime = datetime.now() - timedelta(days=1),
    datetime_end: datetime = datetime.now(),
    limit: int = Query(default=100, le=100),
    page: int = 0,
    pagination: bool = True
) -> Any:
    engine = get_engine_if_register(database)
    with Session(engine) as _session:

        select_query = f"SELECT * from data_{measurement} "
        select_query += f"WHERE channel_id = '{channel_id}' "
        select_query += f"AND time >= '{datetime_from}' "
        select_query += f"AND time <= '{datetime_end}' "

        try:
            count_raw_query = _session.execute(text(select_query.replace("*", "count(*)"))).scalar()
        except Exception:
            raise HTTPException(status_code=404, detail="Relation data-table does not exist")

        total_pages = 0
        if pagination:
            total_pages = ceil(count_raw_query / limit)
            select_query += f" LIMIT {limit} OFFSET {page * limit}"

        raw_query = _session.execute(text(select_query))

        # Convert to Model
        statement = [
            MetaData.from_orm(obj)
            for obj in raw_query
        ]

        if not statement:
            raise HTTPException(status_code=404, detail="No data found")

        return DataPagination(
            data=statement,
            count=count_raw_query,
            total_pages=total_pages,
            actual_page=page,
            pagination=pagination
        )


# http://localhost:5000/api/v1/sincere/localdb_laboratory/download_channel_values/?measurement=develop&datetime_from=2023-06-24T10%3A33%3A52.880906&datetime_end=2024-06-25T10%3A33%3A52.880915&interval=50&file_name=1719311633
# [
#   "a40a50bd-49b0-488c-833f-ad599d00a9b2",
#   "09f712cc-e528-40b0-8d98-98374e9d0e0a"
# ]

@router.put("/{database}/download_channel_values/", response_model= Any)
def download_channel_values(
    session: SessionDep,
    database: str,
    measurement: str,
    datetime_from: datetime = datetime.now() - timedelta(days=1),
    datetime_end: datetime = datetime.now(),
    interval: int = 15,
    file_name: str = int(datetime.now().timestamp()),
    channels_id: list[UUID] = None
) -> Any:
    engine = get_engine_if_register(database)
    with Session(engine) as _session:
        channels_obj_list = [
            (_session.exec(
                select(Channel).where(Channel.channel_id == channel_id)).all()
                ) for channel_id in channels_id
        ]

        dataframes_to_merge = []
        for channel_obj in channels_obj_list:
            if len(channel_obj) == 0:
                break
            select_query = f"SELECT * from data_{measurement} "
            select_query += f"WHERE channel_id = '{channel_obj[0].channel_id}' "
            select_query += f"AND time >= '{datetime_from}' "
            select_query += f"AND time <= '{datetime_end}' "

            try:
                _session.execute(text(select_query.replace("*", "count(*)"))).scalar()
            except Exception:
                raise HTTPException(status_code=404, detail="Relation data-table does not exist")

            raw_query = _session.execute(text(select_query))

            # # Convert to Pandas
            # pd_statement = pd.DataFrame.from_records(
            #     [i.dict() for i in statement]
            # )
            pd_statement = pd.DataFrame(raw_query)

            if pd_statement.empty:
                break
                # raise HTTPException(status_code=404, detail="No data found")

            df = pd_statement.resample(f'{interval}min', on='time')["data_value"]
            # Convert to List
            statement = [
                {'time': obj[0], channel_obj[0].item: round(obj[1].mean(), 2)} for obj in df
            ]
            dataframes_to_merge.append(pd.DataFrame(statement))

        # Merge dataframes into one
        if len(dataframes_to_merge) == 0:
            raise HTTPException(status_code=404, detail="No channels/data found")
        init_dataframes = dataframes_to_merge[0]
        for df in dataframes_to_merge[1:]:
            init_dataframes = pd.merge(init_dataframes, df, on='time', how='outer')

        # Create CSV
        init_dataframes.to_csv(f'{file_name}.csv', index=False)

        return FileResponse(f'{file_name}.csv', media_type="text/csv")


@router.get("/{database}/devices/", response_model=DevicePagination)
def get_devices(
    database: str,
    session: SessionDep,
    limit: int = Query(default=100, le=100),
    page: int = 0,
    pagination: bool = True
) -> Any:
    engine = get_engine_if_register(database)
    with Session(engine) as _session:
        total_pages = 0
        try:
            statement_counting = _session.exec(
                select(func.count(Device.device_id))
            ).one()
        except exc.OperationalError:
            raise HTTPException(status_code=404, detail="Database does not exist")
        #TODO: Set available to True
        # .where(Device.available == True)  # noqa: E712
        statement = (
            select(Device)
        )
        #TODO: Set available to True
        #.where(Device.available == True)  # noqa: E712
        #TODO: Check pagination
        if pagination:
            devices = _session.exec(
                statement.limit(limit).offset(limit * page)
                ).all()
            total_pages = ceil(statement_counting / limit)

        else:
            devices = _session.exec(statement).all()

        if not devices:
            raise HTTPException(status_code=404, detail="No devices found")
        return DevicePagination(
            data=devices,
            count=statement_counting,
            total_pages=total_pages,
            actual_page=page,
            pagination=pagination
        )


@router.get("/{database}/device/{device_id}", response_model=DeviceWithChannelsNoPagination)
def get_device(
    session: SessionDep, database: str, device_id: UUID
) -> Any:
    engine = get_engine_if_register(database)
    with Session(engine) as _session:
        try:
            device = _session.get(Device, device_id)
        except exc.OperationalError:
            raise HTTPException(status_code=404, detail="Database does not exist")
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        return DeviceWithChannelsNoPagination(data=device)


@router.get("/{database}/measurements_aggregator", response_model=SimpleListResponse)
def get_measurements_aggregator(
    session: SessionDep, database: str
) -> Any:
    engine = get_engine_if_register(database)
    with Session(engine) as _session:
        statement = (
            select(Device)
        )
        try:
            raw_statement = _session.exec(statement).all()
        except exc.OperationalError:
            raise HTTPException(status_code=404, detail="Database does not exist")
        pd_statement = pd.DataFrame.from_records(
            [i.dict() for i in raw_statement]
        )
        pd_groupby = pd_statement.groupby(["measurement"])

        def to_dict(group):
            files_no_dup = list(set(group['file'].tolist()))
            return {'measurement': group.name, 'files': files_no_dup}

        list_of_dicts = pd_groupby.apply(to_dict)
        return SimpleListResponse(data=list_of_dicts)


@router.get("/{database}/channels_from_file", response_model=DevicesListWithChannels)
def get_channels_from_file(
    session: SessionDep,
    database: str,
    measurement: str,
    file: str
) -> Any:
    engine = get_engine_if_register(database)
    with Session(engine) as _session:
        statement = (
            select(Device).where(Device.file == file).where(Device.measurement == measurement)
        )
        devices_list = _session.exec(statement).all()
        if not devices_list:
            raise HTTPException(status_code=404, detail="File/Measurement not found")

        return DevicesListWithChannels(data=devices_list)


@router.get("/{database}/writable_channels", response_model=SimpleListResponse)
def get_writable_channels(
    session: SessionDep,
    database: str
) -> Any:
    engine = get_engine_if_register(database)
    with Session(engine) as _session:
        statement = (
            select(Channel).where(Channel.writable)
        )
        channels_list = session.exec(statement).all()
        return SimpleListResponse(data=channels_list)


# @router.post("/set_channel_status", response_model=bool)
# def set_channel_status(
#     session: SessionDep, channel_id: UUID, status: bool
# ) -> Any:
#     return (status)
