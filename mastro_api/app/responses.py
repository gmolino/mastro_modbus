#!/usr/bin/env python3
# from typing import Any

from fastapi import status
from pydantic import BaseModel

from app.models import Device, DeviceWithChannels


class BasePagination(BaseModel):
    count: int | None = None
    total_pages: int | None = None
    actual_page: int | None = None
    pagination: bool = False


class DevicesListWithChannels(BaseModel):
    status: int = status.HTTP_200_OK
    data: list[DeviceWithChannels]


class DeviceWithChannelsNoPagination(BaseModel):
    status: int = status.HTTP_200_OK
    data: DeviceWithChannels


class DevicePagination(BasePagination):
    status: int = status.HTTP_200_OK
    data: list[Device]

class DataPagination(BasePagination):
    status: int = status.HTTP_200_OK
    data: list


class SimpleListResponse(BaseModel):
    status: int = status.HTTP_200_OK
    data: list
