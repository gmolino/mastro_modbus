# -*- coding: utf-8 -*-
import psycopg2
from core.formatter import Logger

from core.config import Settings
config: Settings = Settings()

logger = Logger("connection")

class PostgresTmcClient:
    def __init__(self):

        self.path_connection = f"postgres://{config.postgres_user}:" \
                               f"{config.postgres_password}@{config.postgres_host}:" \
                               f"{config.postgres_port}/{config.postgres_db}"
        self.conn = False

        try:
            self.conn = psycopg2.connect(self.path_connection)

        except Exception as e:
            print(f"Postgres Timescale Connection Error, {e}")
            exit(0)

    def is_connected(self) -> bool:
        return self.conn

    def get_path_connection(self) -> str:
        return self.path_connection
