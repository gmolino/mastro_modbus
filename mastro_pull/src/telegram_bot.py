#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
from core.config import Settings
config: Settings = Settings()

# This class defines a set of emoji symbols as class attributes
class iemojies:
    grinning_face: str = '\U0001F600'
    face_with_symbols_over_mouth: str = '\U0001F92C'
    warning: str = '\U0001F6A8'
    red_circle: str = '\U0001F534'
    green_circle: str = '\U0001F7E2'
    light_bulb: str = '\U0001F4A1'


class telegram_class_bot(iemojies):

    def send_happy_message(self, message = str) -> None:
        requests.post(
            f'https://api.telegram.org/bot{config.bot_token}/sendMessage',
            data={
                'chat_id': config.bot_chat_id,
                'text': f'{iemojies.grinning_face} {message}'
                })


    def send_sad_message(self, message = str) -> None:
        requests.post(
            f'https://api.telegram.org/bot{config.bot_token}/sendMessage',
            data={
                'chat_id': config.bot_chat_id,
                'text': f'{iemojies.face_with_symbols_over_mouth} {message}'
                })


    def send_warning_message(self, message = str) -> None:
        requests.post(
            f'https://api.telegram.org/bot{config.bot_token}/sendMessage',
            data={
                'chat_id': config.bot_chat_id,
                'text': f'{iemojies.warning} {message}'
                })
