# -*- coding: utf-8 -*-
import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    TOKEN: str = os.getenv("TOKEN", 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
    CHAT_ID: int = os.getenv("CHAT_ID", 0000000000)
    TZ: str = os.getenv("TZ", "Europe/Madrid")
    HOST2CHECK: List = [
        {
            'name': 'xxxxxxxx',
            'address': 'xxxxxxxxxxxxxx'
            }
    ]
