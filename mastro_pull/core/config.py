# -*- coding: utf-8 -*-

"""
class from config file
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from rich.console import Console

console = Console()


class Settings(BaseSettings):

    model_config = SettingsConfigDict()

    timezone: str = Field(alias="TIMEZONE", default="Europe/Madrid")

    watchdog: bool = Field(alias="WATCHDOG", default=False)
    timed_watchdog: int = Field(alias="TIMED_WATCHDOG", default=7200)
    bot_token: str | None = Field(alias="TOKEN", default="")
    bot_chat_id: int | None = Field(alias="CHAT_ID", default=0)

    mqtt_insert: bool = Field(alias="MQTT_INSERT", default=True)
    mqtt_host: str = Field(alias="MQTT_HOST", default="172.21.0.4")
    mqtt_queue: str = Field(alias="MQTT_QUEUE", default="biomat_second")

    postgres_insert: bool = Field(alias="PSQL_INSERT", default=False)
    postgres_user: str = Field(alias="PGSQL_USER", default="postgres")
    postgres_password: str = Field(alias="PGSQL_PASSWORD", default="timescalespass")
    postgres_host: str = Field(alias="PGSQL_HOST", default="172.21.0.5")
    postgres_port: int = Field(alias="PGSQL_PORT", default=5432)
    postgres_db: str = Field(alias="PGSQL_DATABASE", default="localdb_laboratory")
    measurement: str = Field(alias="PGSQL_MEASUREMENT", default="test_pydantic")
    
    telegram_warnings: bool = Field(alias="TELEGRAM_WARNINGS", default=False)
    telegram_alive: bool = Field(alias="TELEGRAM_ALIVE", default=False)

    folder_device: str | None = Field(alias="FOLDER_DEVICE", default=None)

    config_mode: str = "environment"
    testing: bool = False

    @classmethod
    def set_testing(self, status) -> None:
        self.testing = status

    @classmethod
    def get_mqtt_queue(self) -> str:
        return self.mqtt_queue
