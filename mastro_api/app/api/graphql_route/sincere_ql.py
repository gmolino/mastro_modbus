from uuid import UUID

import strawberry
from fastapi import (
    HTTPException,
)
from sqlmodel import Session, select
from strawberry.fastapi import GraphQLRouter

from app.api.deps import get_engine_if_register
from app.models import (
    Device,
)

database = "labo_biomat"

@strawberry.type
class Channels:
    id: str
    name: str
    description: str


@strawberry.type
class DeviceQL:
    device_id: UUID
    reference: str
    timer_loop: int
    measurement: str | None
    file: str


def get_devices(db) -> list[DeviceQL]:
    try:
        engine = get_engine_if_register(db)
    except Exception:
        raise HTTPException(status_code=404, detail="Database does not registered")
    with Session(engine) as _session:
        devices = _session.exec(select(Device)).all()
        return devices


@strawberry.type
class Query:
    @strawberry.field
    def devices(self, db: str) -> list[DeviceQL]:
        devices = get_devices(db)
        return devices


class SincereQLAPP:

    schema = strawberry.Schema(query=Query)
    graphql_app = GraphQLRouter(schema)

app = SincereQLAPP()
