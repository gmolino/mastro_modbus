# -*- coding: utf-8 -*-

"""
modbus function codes
"""
import sys
import asyncio
import hashlib
from src.iterate_registers import append_registers, append_error
from src.manage_output import main_output
from src.telegram_bot import telegram_class_bot
from core.formatter import Logger

from core.config import Settings
config: Settings = Settings()

logger = Logger("codes")
telegram_class_bot = telegram_class_bot()

# get_checksum_file
def get_checksum_file(stream):
    md5_hash = hashlib.md5()
    content = open(stream, "rb").read()
    md5_hash.update(content)
    return md5_hash.hexdigest()


# read_registers Asyncio
async def read_registers_async(
    client,
    modbus_device_model,
    modbus_data,
    read_mode,
    repeat_read_mode: int=0
):

    if not client:
        append_error(
            modbus_device_model, modbus_device_model.reference, 
            "Modbus Client error")
        return False
    try:
        match read_mode:
            case "4x":
                registers_from_device = client.read_holding_registers(
                    address=modbus_data.address, 
                    count=modbus_data.count, 
                    slave=modbus_device_model.modbusid
                ).registers
            case "3x":
                registers_from_device = client.read_input_registers(
                    address=modbus_data.address, 
                    count=modbus_data.count, 
                    slave=modbus_device_model.modbusid
                ).registers
            case "0x":
                registers_from_device = client.read_coils(
                    address=modbus_data.address,
                    count=modbus_data.count,
                    slave=modbus_device_model.modbusid
                ).bits
            case _:
                return False

        logger.info(
            f"{modbus_device_model.reference}[{modbus_device_model.gateway}] "
            f"{read_mode}: {registers_from_device}"
        )
        if registers_from_device:
            await append_registers(modbus_device_model, modbus_data, registers_from_device)
        else:
            await append_error(modbus_device_model, "Empty Registers")

        # Sleep if repeat same read mode
        await asyncio.sleep(0.2) if repeat_read_mode > 0 else None

    except Exception as inst:
        await append_error(modbus_device_model, inst)

    return True


async def run_async_client(modbus_device_model, pg_client, lock):
    """
    async client
    """
    reference = modbus_device_model.reference  # Return name
    client = modbus_device_model.client  # Return client
    # devices_directory = os.path.dirname(os.path.realpath("__file__")) + "/devices"
    try:
        while True:
            lock.acquire()
            try:
                client.connect()
                # checksum = f"{devices_directory}/{modbus_device_obj.file_tag}.yaml"
                # logger.info("File => %s", get_checksum_file(checksum))

                # Read registers
                async def request_registers(read_mode):
                    registers_by_mode = modbus_device_model.get_registers_by_read_mode(read_mode)
                    [
                        await read_registers_async(
                            client,
                            modbus_device_model,
                            modbus_data,
                            read_mode,
                            repeat_read_mode= len(registers_by_mode)
                        )
                        for modbus_data in registers_by_mode
                    ]

                # Read holding_registers del gw -> 4x
                if modbus_device_model._4x:
                    await request_registers('4x')
                # Read input_registers del gw -> 3x
                if modbus_device_model._3x:
                    await request_registers('3x')
                # Read coil_registers del gw -> 0x
                if modbus_device_model._0x:
                    await request_registers('0x')

                client.close()

                # Main OUTPUT
                await main_output(modbus_device_model, pg_client)
                modbus_device_model.tag_registers = []
                modbus_device_model.errors = []

            except Exception as error:
                logger.error(f"{reference}: {error}")
                append_error(modbus_device_model, error)

            finally:
                lock.release()

            await asyncio.sleep(int(modbus_device_model.loop))

    except KeyboardInterrupt:
        await client.close()
        sys.exit(0)


async def run_async_watchdog(lock):
    """
    async watchdog
    """
    while True:
        try:
            lock.acquire()
            logger.info(f"Watchdog {config.measurement}: I am alive!")
            if config.telegram_alive is True:
                telegram_class_bot.send_happy_message(
                    f'[{config.measurement}] I am alive!')

        except Exception as inst:
            logger.error(f"Watchdog error: {inst}")
        finally:
            lock.release()

        await asyncio.sleep(int(config.timed_watchdog))


def modbus_process_loop(modbus_device_model, pg_client, lock=None):
    asyncio.run(run_async_client(modbus_device_model, pg_client, lock))


def watchdog_process_loop(lock=None):
    asyncio.run(run_async_watchdog(lock))
