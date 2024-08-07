# -*- coding: utf-8 -*-
from core.formatter import Logger
from src.mqtt_publish_class import check_mqtt_connection

from core.config import Settings
config: Settings = Settings()

logger = Logger("out")


@check_mqtt_connection
def send_mqtt_values(modbus_device_model):
    mqtt_object = modbus_device_model.rabbit_publisher
    mqtt_object.channel
    mqtt_object.connect

    model_dump_response = modbus_device_model.model_dump()
    try:
        mqtt_object.publish(
            response={
                'response': model_dump_response.get('tag_registers')
            },
            routing_key="info.values")
    except Exception as error:
        logger.error(f"RabbitMQ error: {error}")
        mqtt_object.close


async def main_output(modbus_device_model, pg_client):
    if modbus_device_model.errors:
        logger.warning(f"{modbus_device_model.reference}: {modbus_device_model.errors}")
        # insert alert in db
        # if config.testing is False:
        #     await modbus_device_obj.insert_or_update_alert(pg_client)

        # MQTT ERRORS
        # if config.mqtt_insert and config.testing is False:
        #     #TODO ajustar mensage de alerta para mqtt
        #     mqtt_object = modbus_device_model.rabbit_publisher
        #     mqtt_object.channel
        #     if mqtt_object.is_alive is False:
        #         mqtt_object.connect
        #     if mqtt_object.is_alive is False:
        #         logger.warning("MQTT Client not alive")
        #     else:
        #         mqtt_object.publish(
        #             response=f"{device_registers.get('errors')[0]['detail']}",
        #             routing_key="info.alerts"
        #         )
        #         mqtt_object.close

    if modbus_device_model.tag_registers:
        logger.debug(f"{modbus_device_model.reference}: {modbus_device_model.tag_registers}")

        # TIMESCALE DB
        if config.postgres_insert and config.testing is False:
            await modbus_device_model.db_insert_values(pg_client)

        # MQTT RESPONSES
        if config.mqtt_insert and config.testing is False:
            send_mqtt_values(modbus_device_model)