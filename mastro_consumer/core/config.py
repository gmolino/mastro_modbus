# -*- coding: utf-8 -*-

from typing import Optional #, Union, Any, Dict, List
from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_host: str = Field(alias="PGSQL_HOST", default="172.21.0.5")
    postgres_port: int = Field(alias="PGSQL_PORT", default=5432)
    postgres_user: str = Field(alias="PGSQL_USER", default="postgres")
    postgres_password: str = Field(alias="PGSQL_PASSWORD", default="timescalespass")
    postgres_db: str = Field(alias="PGSQL_DATABASE", default="biomat_testing_consumer")
    postgres_insert: bool = Field(alias="PGSQL_INSERT", default=True)

    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    mqtt_host: str = Field(alias="MQTT_HOST", default="localhost")
    mqtt_queue: str = Field(alias="MQTT_QUEUE", default="biomat_second")
    mqtt_insert: bool = Field(alias="MQTT_INSERT", default=True)

    timezone: str = Field(alias="TIMEZONE", default="Europe/Madrid")
settings = Settings()
