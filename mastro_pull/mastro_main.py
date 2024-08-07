# -*- coding: utf-8 -*-

"""
main loop modbus devices
"""

import os
import time
from multiprocessing import Process, Lock
import asyncio
import sys
import argparse
from typing import List
from rich import print
from rich.console import Console
import justpy as jp

from src.modbus_function_codes import modbus_process_loop, watchdog_process_loop
from src.mqtt_publish_class import check_mqtt_connection
from src.mastro_device_class import (
    ModbusNetworkMap, 
    ModbusDataCoil,
    ModbusDataInput,
    ModbusDataHolding,
    ModbusDeviceModel
)

from core.formatter import Logger
from db.connections import PostgresTmcClient
from db.generator import grafana_generator
from src.app_framework import mastro_framework, add_device

from core.config import Settings
config: Settings = Settings()

console = Console()
logger = Logger("mastro")
dir_path = os.path.dirname(os.path.realpath("__file__")) + "/core/"

TAG_VERSION = "v2.7.2"

@check_mqtt_connection
def send_mqtt_channels_and_devices(modbus_device_model):

    mqtt_object = modbus_device_model.rabbit_publisher
    mqtt_object.channel
    mqtt_object.connect

    # Insert device
    mqtt_object.publish(
        response=modbus_device_model.get_device,
        routing_key="info.device"
    )

    # Publish Channels
    dump_channels = [
        channel.model_dump() for channel in modbus_device_model.get_channels
    ]
    mqtt_object.publish(
        response={
            'reference': modbus_device_model.reference,
            'file_tag': modbus_device_model.file,
            'channels': dump_channels
        },
        routing_key='info.channels'
    )
    mqtt_object.close


async def main(args_parse) -> None:
    if args_parse.config:
        console.log(config.model_dump())
        sys.exit(0)

    if args_parse.test:
        config.set_testing(True)

    loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
    lock: Lock = Lock()

    modbus_map_obj = ModbusNetworkMap()
    modbus_devices = modbus_map_obj.get_modbus_devices()
    interface = modbus_map_obj.get_interface()

    # last_commit = os.popen("git rev-parse HEAD").read().strip()
    # current_tag = os.popen("git describe --tags").read().strip()

    # Args show modbus map
    if args_parse.modbus:
        modbus_map_obj.echo_console()
        sys.exit(0)

    with open(dir_path + "logo", "r", encoding="utf-8") as logo:
        logo_contents = logo.read()
        print(f"[yellow]{logo_contents}{TAG_VERSION}[/yellow]\n")
        logo.close()
    
    logger.info(f"Config Mode: {config.config_mode} | "
                f"Testing: {config.testing} | "
                f"Watchdog: {config.watchdog}[{config.timed_watchdog}] ")
    logger.info(f"Mastro {TAG_VERSION}")
    logger.info(
        f"mqtt://{config.mqtt_host}:5672/{config.mqtt_queue}[{config.mqtt_insert}]")
    logger.info(
        f"postgres://{config.postgres_user}:******@"
        f"{config.postgres_host}:{config.postgres_port}/"
        f"{config.postgres_db}[{config.postgres_insert}]")

    # POSTGRES
    pg_client: PostgresTmcClient = PostgresTmcClient()

    if args_parse.generator:
        grafana_generator(pg_client)
        sys.exit(0)

    processes: List[Process] = []
    for device_sensor_dict in modbus_devices:

        modbus_device_model = ModbusDeviceModel(
            measurement=config.measurement,
            mqtt_host=config.mqtt_host,
            mqtt_insert=config.mqtt_insert,
            mqtt_queue=config.mqtt_queue,
            interface=interface,
            reference=device_sensor_dict.get('reference'),
            gateway=device_sensor_dict.get('gateway'),
            modbusid=device_sensor_dict.get('modbusid'),
            loop=device_sensor_dict.get('loop'),
            file=device_sensor_dict.get('file')
        )

        modbus_device_model._3x = [
                ModbusDataInput(**register) for register in device_sensor_dict.get('3x')
            ] if device_sensor_dict.get('3x') else []
        modbus_device_model._4x = [
                ModbusDataHolding(**register) for register in device_sensor_dict.get('4x')
            ] if device_sensor_dict.get('4x') else []
        modbus_device_model._0x = [
                ModbusDataCoil(**register) for register in device_sensor_dict.get('0x')
            ] if device_sensor_dict.get('0x') else []

        # POSTGRES - Inserta los canales en las tablas
        await modbus_device_model.db_insert_device(pg_client)
        await modbus_device_model.create_measurement_table(pg_client)
        await modbus_device_model.db_insert_channels(pg_client)

        # MQTT
        if config.mqtt_insert and config.testing is False:
            send_mqtt_channels_and_devices(modbus_device_model)

        # Modbus
        processes.append(
            Process(
                target=modbus_process_loop,
                args=(
                    modbus_device_model,
                    pg_client,
                    lock,
                ),
            )
        )

        add_device(modbus_device_model)

    # If Watchdog is enabled add the new process
    if config.watchdog is True:
        processes.append(
            Process(
                target=watchdog_process_loop,
                args=(
                    lock,
                ),
            )
        )

    # Framework (JustPy) - Webserver
    if True:
        processes.append(
            Process(
                target=jp.justpy,
                args=(
                    mastro_framework,
                ),
            )
        )
    
    for p in processes:
        p.start()
        time.sleep(1.3)
    for p in processes:
        p.join()
    processes.clear()
    loop.close()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Mastro Scada: Modbus Process loop')
    parser.add_argument('-t', '--test', action='store_true', help='Test mode')
    parser.add_argument('-c', '--config', action='store_true', help='Show config file')
    parser.add_argument('-m', '--modbus', action='store_true', help='Show modbus map')
    parser.add_argument('-e', '--env', action='store_true', help='Executed with Environment variables')
    parser.add_argument('-g', '--generator', action='store_true', help='Grafana Sql generator')

    args_parse = parser.parse_args()
    asyncio.run(main(args_parse))
