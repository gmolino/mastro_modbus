# -*- coding: utf-8 -*-

"""
enqueue registers to rabbitmq
"""

import json
import pika
from core.formatter import Logger
from pydantic import BaseModel
from typing import Any

logger = Logger("pub/sub")
TOPIC_EXCHANGE = "topic_reinvent"


class RabbitPublisher(BaseModel):
    connection: object = None
    channel: Any = None

    deliveries: dict = None
    acked: dict = None
    nacked: dict = None
    message_number: int = None
    stopping: bool = False

    mqtt_host: str = None
    mqtt_queue: str = None
    mqtt_insert: bool = False

    @property
    def connect(self):
        if self.mqtt_insert:
            try:
                credentials = pika.PlainCredentials('guest', 'guest')
                connection = pika.BlockingConnection(
                    pika.ConnectionParameters(
                        f'{self.mqtt_host}',
                        5672,
                        '/',
                        credentials
                    )
                )
                self.connection = connection
                channel = connection.channel()
                channel.exchange_declare(
                    exchange=TOPIC_EXCHANGE,
                    exchange_type="topic",
                    durable=True
                )
                channel.queue_declare(
                    queue=self.mqtt_queue, 
                    durable=True, 
                    auto_delete=False
                )
                channel.confirm_delivery()
                self.channel = channel
                return channel

            except Exception as error:
                logger.error(f"Broker unable to connect: {error}")
                return False

    def channel(self):
        return self.channel

    @property
    def close(self):
        self.connection.close()

    def publish(self, response: dict = None, routing_key="info.values") -> None:
        """rabbit insert function"""
        try:
            self.channel.basic_publish(
                exchange=TOPIC_EXCHANGE,
                routing_key=routing_key,
                body=json.dumps(response).encode('utf-8'),
                properties=pika.BasicProperties(
                    delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
                )
            )
            logger.info(f"MQTT published confirmed [{routing_key}]")
        except pika.exceptions.UnroutableError as error:
            logger.error(f"MQTT could not be published: {error}")
        except pika.exceptions.StreamLostError as error:
            logger.error(f"MQTT Stream lost: {error}")
        except Exception as error:
            logger.error(repr(error))


    @property
    def is_alive(self):
        try:
            if self.channel.is_open:
                return True
            else:
                return False
        except AttributeError:
            return False

"""
A decorator that checks the connection status of the MQTT object before executing the given function. 
If the MQTT object is not alive, it tries to reconnect. 
If the MQTT object is alive, it executes the given function; otherwise, it logs a warning message. 
"""
def check_mqtt_connection(function):
    def wrapper(*args, **kwargs):
        mqtt_object = args[0].rabbit_publisher
        mqtt_object.channel

        if mqtt_object.is_alive is False:
            mqtt_object.connect
        if mqtt_object.is_alive is True:
            return function(*args, **kwargs)
        else:
            logger.warning("MQTT Client not alive")
            
    return wrapper
