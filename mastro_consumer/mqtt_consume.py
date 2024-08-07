# -*- coding: utf-8 -*

import pika
import json
import sys
from rich.console import Console
from core.db_consume import PostgresConsumerClass
from core.config import Settings
from core.formatter import Logger

config: Settings = Settings()
console = Console()

logger = Logger("consumer")
TOPIC_EXCHANGE = "topic_reinvent"

class MastroConsumer:
    def __init__(self):
        self._mqtt_host = config.mqtt_host
        self._queue = config.mqtt_queue
        self._topic_exchange = TOPIC_EXCHANGE
        self.postgres_insert = config.postgres_insert
        if config.postgres_insert:
            self._postgres_consumer = PostgresConsumerClass()
            # Ejecuta consulta con lista de dispositivos y canales
            self._postgres_consumer.device_channel_relations()
        else:
            self._postgres_consumer = None

    def connect(self):
        logger.debug(f"Connecting to {self._mqtt_host}...")
        credentials = pika.PlainCredentials("guest", "guest")
        parameters = pika.ConnectionParameters(self._mqtt_host, 5672, "/", credentials)
        logger.debug(parameters)

        def on_message(ch, method, properties, body):
            pg_relations = self._postgres_consumer.device_relations_reference_id
            data = json.loads(body.decode('utf-8'))

            match method.routing_key:
                case "info.values":
                    response_list = data.get("response")
                    for each_response in response_list:
                        measurement = each_response.get("measurement")
                        logger.info(f"[{method.routing_key}]{self._queue}: {each_response}")
                        # Insert in DB
                        if self.postgres_insert and pg_relations:
                            if measurement not in self._postgres_consumer.created_table_list:
                                self._postgres_consumer.create_measurement_table(measurement)
                            self._postgres_consumer.db_insert_values(each_response)

                case "info.alerts":
                    logger.info(f"[{method.routing_key}]{each_response}")

                case"info.channels":
                    logger.info(f"[{method.routing_key}]{data}")
                    if self.postgres_insert:
                        self._postgres_consumer.db_insert_channels(data)
                        self._postgres_consumer.device_channel_relations()

                case "info.device":
                    logger.info(f"[{method.routing_key}]{data}")
                    if self.postgres_insert:
                        self._postgres_consumer.db_insert_device(data)
                        self._postgres_consumer.device_channel_relations()

                case _:
                    logger.info(f"[{method.routing_key}]{data}")

        try:
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()
            channel.exchange_declare(
                exchange=self._topic_exchange,
                exchange_type="topic",
                durable=True
            )
            channel.queue_declare(self._queue, exclusive=False, durable=True)
            channel.queue_bind(
                exchange=self._topic_exchange,
                queue=self._queue,
                routing_key="info.#"
            )

            logger.info(f"[*]Msgs to {self._queue}. "
                    f"Mqtt: {self._mqtt_host}. Queue: {self._queue}")

            channel.basic_consume(
                queue=self._queue,
                on_message_callback=on_message,
                auto_ack=True
            )
            channel.start_consuming()

        except Exception as err:
            logger.error(f"MQTT Error: {err}")


def create_worker() -> None:
    logger.info("Starting Mastro Consumer Service...")

    try:
        mastro_consumer = MastroConsumer()
        mastro_consumer.connect()
    except KeyboardInterrupt:
        print("Interrupted...")
        sys.exit(0)


if __name__ == "__main__":
    create_worker()
