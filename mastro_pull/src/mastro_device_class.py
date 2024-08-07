# -*- coding: utf-8 -*-

"""
modbus network class
"""
import sys
import os
import logging
import psycopg2
import pendulum
from pymodbus.client import (
    AsyncModbusSerialClient,
    # AsyncModbusTcpClient,
    ModbusTcpClient,
)
import yaml
# from uuid import UUID
from typing import List
from pydantic import BaseModel
from psycopg2 import errors
from src.mqtt_publish_class import RabbitPublisher
from core.config import Settings
config: Settings = Settings()

logger = logging.getLogger("mastro")

PORT = 502
BAUDRATE = 9600
TIMER_LOOP = 30
TIMEOUT = 2


class ModbusNetworkMap:
    def __init__(self):
        if config.folder_device is None or config.folder_device == "":
            folder_device = "devices"
            devices_directory = os.path.dirname(
                os.path.realpath("__file__")) + "/devices"
        else:
            folder_device = config.folder_device
            devices_directory = os.path.dirname(
                os.path.realpath("__file__")) + f"/devices/{folder_device}"

        map_devices = []
        any_yaml = False
        try:
            for yaml_file in os.listdir(devices_directory):
                if yaml_file.endswith(".yaml") or yaml_file.endswith(".yml"):
                    any_yaml = True
                    with open(f"{devices_directory}/{yaml_file}", "r") as stream:
                        yaml_stream = yaml.safe_load(stream)
                        try:
                            map_file = yaml_stream.get("devices")
                            for i in map_file:
                                i["file"] = yaml_file[: yaml_file.find(".")]
                            map_devices.extend(map_file)
                        except yaml.YAMLError as error:
                            logger.critical(error)
                            sys.exit(0)

                        if "interface" in yaml_stream:
                            self.interface = (yaml_stream.get("interface"), 0)
                        else:
                            self.interface = ("", 0)
        except FileNotFoundError:
            logger.critical(f"ERROR: /{folder_device}/ folder missing")
            exit(0)
        if not any_yaml:
            logger.critical("ERROR: yaml files missing")
            exit(0)
        self.modbus_net = map_devices

    def get_modbus_devices(self):

        for device in self.modbus_net:
            if "clients" in device:
                for end_device in device["clients"]:

                    for tag in ["gateway", "port", "loop"]:
                        try:
                            end_device.update({tag: device[tag]})
                        except KeyError:
                            if tag == "port":
                                end_device.update({tag: PORT})
                            elif tag == "loop":
                                end_device.update({tag: TIMER_LOOP})
                            else:
                                pass
                    end_device.update({"file": device["file"]})
                    end_device.update({"interface": self.interface})
                    self.modbus_net.append(end_device)
                device.pop("clients")

        # Elimina dispositivos sin 3x o 4x, el device con endpoints
        for item, device in enumerate(self.modbus_net):
            if "3x" not in device and "4x" not in device:
                self.modbus_net.pop(item)

        return self.modbus_net

    def get_interface(self):
        return self.interface

    def echo_console(self):
        logger.info(f"{self.modbus_net}")


class DeviceConfig(BaseModel):
    measurement: str
    mqtt_host: str
    mqtt_insert: bool
    mqtt_queue: str
    interface: tuple = ("", 0)

class Channel(BaseModel):
    ch: int
    item: str
    unit: str = None
    const: float = None
    errorcode: int = None
    unsigned: bool = False
    formula: str = None
    alarm: list = []
    offset: float = 0.0
    writable: bool = False
    virtual_channel: int = 0

class ModbusData(BaseModel):
    address: int
    count: int
    channels: List[Channel]

class ModbusDataCoil(ModbusData):
    memory_area: int = 0

class ModbusDataInput(ModbusData):
    memory_area: int = 30000

class ModbusDataHolding(ModbusData):
    memory_area: int = 40000


class ResponseTag(BaseModel):
    value: dict = {}
    timestamp: str = pendulum.now('Europe/Madrid')
    out_of_ranges: list = []
    alarms: list = []
    timescale: list = []
    measurement: str
    file: str
    reference: str

class ModbusDeviceModel(DeviceConfig):
    device_id: str = None
    reference: str
    gateway: str
    port: int = PORT
    modbusid: int
    loop: int
    _0x: List[ModbusData] = []
    _3x: List[ModbusData] = []
    _4x: List[ModbusData] = []
    file: str

    errors: list = []
    online: bool = True
    tag_registers: List[ResponseTag] = []
    sensornet_update: bool = False
    sensor_channels: dict = {}
    relation_item_tms_id: dict = {}


    def get_registers_by_read_mode(self, read_mode):
        if read_mode == "3x":
            return self._3x
        elif read_mode == "4x":
            return self._4x
        elif read_mode == "0x":
            return self._0x
        else:
            return []

    # PROPERTIES
    @property
    def get_device(self):
        return {
            'reference': self.reference,
            'gateway': self.gateway,
            'file_tag': self.file,
            'timer_loop': self.loop,
            'measurement': self.measurement
        }

    @property
    def rabbit_publisher(self):
        return RabbitPublisher(
            mqtt_host=self.mqtt_host,
            mqtt_queue=self.mqtt_queue,
            mqtt_insert=self.mqtt_insert
        )

    @property
    def get_channels(self):
        channels = []
        for modbus_data in self._3x + self._4x + self._0x:
            for channel in modbus_data.channels:
                channels.append(channel)
        return channels

    @property
    def client(self):
        if self.gateway[:1] == "/":
            return AsyncModbusSerialClient(
                self.gateway,  # args.port,
                # Common optional parameters:
                #    framer=ModbusRtuFramer,
                timeout=TIMEOUT,
                #    retries=3,
                #    retry_on_empty=False,
                #    close_comm_on_error=False,
                #    strict=True,
                # Serial setup parameters
                baudrate=self.baudrate,
                #    bytesize=8,
                #    parity="N",
                #    stopbits=1,
                #    handle_local_echo=False,
            )
        else:
            # self.client = AsyncModbusTcpClient(
            #     self.gateway,
            #     port=self.port,  # on which port
            #     # Common optional parameters:
            #     # framer=args.framer,
            #     timeout=TIMEOUT,
            #     #    retries=3,
            #     #    retry_on_empty=False,
            #     #    close_comm_on_error=False,
            #     #    strict=True,
            #     # TCP setup parameters
            #     #    source_address=("localhost", 0),
            # )
            return ModbusTcpClient(
                host=self.gateway,
                port=self.port,
                source_address=self.interface,
                timeout=TIMEOUT,
            )


    # ASYNC QUERY FUNCTIONS
    async def db_insert_device(self, pg_client):
        query = (
            f"INSERT INTO devices (file, reference, gateway, timer_loop, measurement, available) "
            f"VALUES ('{self.file}', '{self.reference}', '{self.gateway}', "
            f"'{self.loop}', '{self.measurement}', true) "
            f"ON CONFLICT (reference) DO UPDATE SET file='{self.file}', "
            f"gateway='{self.gateway}', timer_loop={self.loop} "
            f"RETURNING device_id;"
        )
        print(query)
        try:
            conn = pg_client.conn
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()
            self.device_id = cursor.fetchone()[0]

        except errors.UndefinedTable as e:
            logger.critical(e)

    async def create_measurement_table(self, pg_client):
        conn = pg_client.conn
        cursor = conn.cursor()
        try:
            cursor.execute(
                f"CREATE TABLE IF NOT EXISTS public.data_{self.measurement} "
                f"(time timestamptz NOT NULL, channel_id uuid NULL, "
                f"data_value float8 NULL, measurement varchar NULL);"
                f"ALTER TABLE public.data_{self.measurement} ADD CONSTRAINT sensor_data_channel_id_fkey "
                f"FOREIGN KEY (channel_id) REFERENCES public.channels(channel_id);"
            )

        except (Exception, psycopg2.Error) as error:
            logger.warning(error)
        conn.commit()

    async def db_insert_channels(self, pg_client) -> None:
        for modbus_data in self._3x + self._4x + self._0x:
            for channel in modbus_data.channels:
                #TODO: ajustar para channels de dos canales
                # for each in channel:
                #     each_ch = each.get('ch')[0] if isinstance(each.get('ch'), list) else each.get('ch')

                channel.virtual_channel = modbus_data.memory_area + modbus_data.address + channel.ch
                query = (
                    f"INSERT INTO channels (device_id, channel, unit, item, writable) "
                    f"SELECT '{self.device_id}', {channel.virtual_channel}, '{channel.unit}', "
                    f"'{channel.item}', {channel.writable} "
                    f"WHERE NOT EXISTS (SELECT device_id FROM channels WHERE "
                    f"device_id='{self.device_id}' AND channel={channel.virtual_channel}) "
                    f"RETURNING channel_id;"
                )
                try:
                    conn = pg_client.conn
                    cursor = conn.cursor()
                    cursor.execute(query)
                    conn.commit()
                    try:
                        channel_id = cursor.fetchone()[0]
                    except TypeError:
                        query = (
                            f"UPDATE channels SET (unit, item, writable) = "
                            f"('{channel.unit}', '{channel.item}', {channel.writable}) "
                            f"WHERE device_id='{self.device_id}' AND channel={channel.virtual_channel} "
                            f"RETURNING channel_id;"
                        )
                        cursor.execute(query)
                        conn.commit()
                        channel_id = cursor.fetchone()[0]
                    self.relation_item_tms_id.update({channel.ch: channel_id})

                except errors.UndefinedTable as e:
                    logger.critical(e)

    async def db_insert_values(self, pg_client):
        conn = pg_client.conn
        cursor = conn.cursor()
        for each in self.tag_registers:
            time_tsc = pendulum.parse(str(each.timestamp))
            for sensor in each.timescale:
                try:
                    cursor.execute(
                        f"INSERT INTO public.data_{self.measurement} "
                        f"(channel_id, time, data_value, measurement) "
                        f"VALUES ('{sensor[0]}', '{time_tsc}', {sensor[1]}, '{self.measurement}');"
                    )
                except (Exception, psycopg2.Error) as error:
                    logger.critical(error.pgerror)
            conn.commit()
