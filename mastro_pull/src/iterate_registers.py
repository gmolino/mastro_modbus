# -*- coding: utf-8 -*-

import pendulum
import numpy as np
from src.telegram_bot import telegram_class_bot
from src.mastro_device_class import ResponseTag

from core.config import Settings
config: Settings = Settings()

telegram_class_bot = telegram_class_bot()

def get_timestamp():
    now = pendulum.now('Europe/Madrid')
    return str(now)


# Itera por los registros recogidos del sensor
'''
    modbus_device_model = modelo del device
    modbus_data = canales del dispositivo consultado
    registers_from_device = registros recogidos del sensor
'''

async def append_registers(modbus_device_model, modbus_data, registers_from_device) -> None:
    items_with_their_value: dict = {}
    uuids_with_their_value: list = []
    out_of_ranges: list = []
    alarms: list = []

    #ch=3 item='TC1' unit='ºC' const=0.1 errorcode=-1
    for channel_requested in modbus_data.channels:
        if isinstance(channel_requested.ch, int):
            channel_value = registers_from_device[channel_requested.ch]
        elif isinstance(channel_requested.ch, list):
            # Si dos canales en lista, transforma en 32 bits.
            channel_value = registers_from_device[channel_requested.ch[0]]
            channel_value_32 = registers_from_device[channel_requested.ch[1]]
            tmp = channel_value << 16 | channel_value_32
            if channel_requested.unsigned is True:
                float_value = float(tmp)
            else:
                float_value = float(np.int32(tmp))
        else:
            channel_value = None

        # Código de error modbus o null
        if (
            channel_requested.errorcode == int(np.int16(channel_value))
            or channel_value is None
        ):
            alarms.append(channel_requested.item)
            float_value = None

        else:
            if channel_requested.unsigned is True:
                float_value = float(channel_value)
            else:
                float_value = float(np.int16(channel_value))

            # si formula sustituye x y convierte a formula matematica
            if channel_requested.formula is not None:
                float_value = eval(channel_requested.formula.replace("x", str(float_value)))

            # multiplica por constante
            if channel_requested.const is not None:
                float_value = float_value * channel_requested.const

            # aplicar offset
            float_value = float_value + channel_requested.offset

            # si rango de alarmas
            if channel_requested.alarm:
                range_alarm = channel_requested.alarm
                if not (range_alarm[0] <= float_value <= range_alarm[1]):
                    out_of_ranges.append(channel_requested.item)

        if float_value is not None:
            float_value = round(float_value, 3)
            items_with_their_value.update(
                {
                    channel_requested.item: float_value
                }
            )

            uuids_with_their_value.append(
                (modbus_device_model.relation_item_tms_id.get(channel_requested.ch), float_value)
            )

    modbus_device_model.tag_registers.append(
        ResponseTag(
            value=items_with_their_value,
            timestamp=get_timestamp(),
            out_of_ranges=out_of_ranges,
            alarms=alarms,
            file=modbus_device_model.file,
            timescale=uuids_with_their_value,
            measurement=modbus_device_model.measurement,
            reference=modbus_device_model.reference
        )
    )

    # Set online to true si no hay error and Telegram message
    if modbus_device_model.online is False:
        modbus_device_model.online = True
        if config.telegram_warnings is True:
            telegram_class_bot.send_happy_message(
                f'[{modbus_device_model.reference}] - {modbus_device_model.measurement} - ONLINE')


async def append_error(modbus_device_model, error) -> None:
    tag_register = {"detail": error, "timestamp": get_timestamp()}
    modbus_device_model.errors.append(tag_register)

    if modbus_device_model.online is True:
        #Set online to false si hay error and Telegram message
        modbus_device_model.online = False
        if config.telegram_warnings is True:
            telegram_class_bot.send_sad_message(
                f"[{modbus_device_model.reference}] - {modbus_device_model.measurement} - {error}")
