from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel
from sqlmodel import Field, Relationship, SQLModel


# Shared properties
# TODO replace email str with EmailStr when sqlmodel supports it
class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = None


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str


# TODO replace email str with EmailStr when sqlmodel supports it
class UserRegister(SQLModel):
    email: str
    password: str
    full_name: str | None = None


# Properties to receive via API on update, all are optional
# TODO replace email str with EmailStr when sqlmodel supports it
class UserUpdate(UserBase):
    email: str | None = None  # type: ignore
    password: str | None = None


# TODO replace email str with EmailStr when sqlmodel supports it
class UserUpdateMe(SQLModel):
    full_name: str | None = None
    email: str | None = None


class UpdatePassword(SQLModel):
    current_password: str
    new_password: str


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: UUID | None = Field(default=None, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner")


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
class ItemBase(SQLModel):
    title: str
    description: str | None = None


# Properties to receive on item creation
class ItemCreate(ItemBase):
    title: str


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: str | None = None  # type: ignore


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: UUID | None = Field(default=None, primary_key=True)
    title: str
    owner_id: UUID | None = Field(default=None, foreign_key="user.id", nullable=False)
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: UUID
    owner_id: UUID


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str

########################################################
## MASTRO MODELS
## DEVICE AND CHANNEL
########################################################

class MetaData(SQLModel):

    channel_id: UUID = Field(
        foreign_key="channels.channel_id", primary_key=True)
    data_value: float
    measurement: str
    time: datetime | None = Field(primary_key=True)

    class Config:
        from_attributes = True


# DEVICE MODEL
class DeviceBase(SQLModel):
    reference: str = Field(unique=True)
    timer_loop: int
    measurement: str | None = None
    file: str | None = None
    gateway: str | None = None
    available: bool | None = None
    last_access: datetime | None = None


class Device(DeviceBase, table=True):

    __tablename__ = "devices"

    device_id: UUID | None = Field(
        default=uuid4(), primary_key=True)
    channels: list["Channel"] = Relationship(back_populates="device")

class DevicePublic(DeviceBase):
    device_id: UUID


# CHANNEL MODEL
class ChannelBase(SQLModel):
    device_id: UUID | None = Field(
        default=None, foreign_key="devices.device_id")
    channel: int
    unit: str
    item: str
    constant: float | None = None
    writable: bool = False

class Channel(ChannelBase, table=True):

    __tablename__ = "channels"

    channel_id: UUID | None = Field(
        default=uuid4(), primary_key=True)
    device: Device | None = Relationship(back_populates="channels")

class ChannelPublic(ChannelBase):
    channel_id: UUID

class ChannelPrivate(SQLModel):
    channel_id: UUID

# ALERT MODEL
class AlertBase(SQLModel):
    device_id: UUID
    channel_id: UUID
    message: str

class Alert(AlertBase, table=True):

    __tablename__ = "alerts"

    alert_id: UUID | None = Field(
        default=uuid4(), primary_key=True)

class AlertPublic(AlertBase):
    alert_id: UUID


# DEVICE WITH CHANNELS RELATIONSHIP
class DeviceWithChannels(DeviceBase):
    channels: list[Channel] = []


# class MeasurementsFilesRelation(BaseModel):
#     measurement : str
#     file: [str]
