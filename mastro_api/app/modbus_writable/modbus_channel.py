from uuid import UUID

from pydantic import BaseModel


class ModbusData(BaseModel):
    channel_id: UUID
    channel: int
    status: bool
    device_id: UUID = None
    gateway: str = None
    port: int = 5432
    modbusid: int = 1
