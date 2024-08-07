# -*- coding: utf-8 -*
import sys
import psycopg2
import pendulum
from psycopg2 import errors

from core.config import Settings
config: Settings = Settings()

def get_value_in_list_channel(channel_value):
    if not isinstance(channel_value, int):
        channel_value = channel_value[0]
    return channel_value


class PostgresConsumerClass:
    def __init__(self):
        self.postgres_user = config.postgres_user
        self.postgres_host = config.postgres_host
        self.postgres_password = config.postgres_password
        self.postgres_port = config.postgres_port
        self.postgres_db = config.postgres_db
        self.relation_item_tms_id: dict = {}
        self.created_table_list = []
        self.device_relations_reference_id = None
        self.path_connection = f"postgres://{self.postgres_user}:" \
                               f"{self.postgres_password}@{self.postgres_host}:" \
                               f"{self.postgres_port}/{self.postgres_db}"
        print(self.path_connection)

        try:
            self.conn = psycopg2.connect(self.path_connection)
            print(self.conn)
        except Exception as e:
            print(f"Postgres Timescale Connection Error, {e}")
            sys.exit(0)

    # Relación entre dispositivos y canales
    def device_channel_relations(self):
        conn = self.conn
        cursor = conn.cursor()
        cursor.execute('SELECT channel_id, dv.device_id, item, reference, measurement '
                       'FROM channels ch INNER JOIN devices dv ON ch.device_id = dv.device_id;')
        self.device_relations_reference_id = cursor.fetchall()

    def db_insert_values(self, register):
        conn = self.conn
        cursor = conn.cursor()
        for sensor in register.get("value").items():
            channel_id = list(filter(
                lambda x: x[3] == register.get('reference') and x[2] == sensor[0] in x,
                self.device_relations_reference_id)
            )[-1]
            try:
                cursor.execute(
                    f"INSERT INTO public.data_{register.get('measurement')} "
                    f"(channel_id, time, data_value, measurement) "
                    f"VALUES ('{channel_id[0]}', '{pendulum.parse(register.get('timestamp'))}', "
                    f"{sensor[1]}, '{register.get('measurement')}');"
                )
            except (Exception, psycopg2.Error) as error:
                print(error)
        conn.commit()

    def create_measurement_table(self, measurement):
        conn = self.conn
        cursor = conn.cursor()
        try:
            cursor.execute(
                f"CREATE TABLE IF NOT EXISTS public.data_{measurement} "
                f"(time timestamptz NOT NULL, channel_id uuid NULL, "
                f"data_value float8 NULL, measurement varchar NULL);"
            )
            # f"ALTER TABLE public.data_{measurement} ADD CONSTRAINT sensor_data_channel_id_fkey "
            # f"FOREIGN KEY (channel_id) REFERENCES public.channels(channel_id);"
            self.created_table_list.append(measurement)

        except (Exception, psycopg2.Error) as error:
            print(error.pgerror)
        conn.commit()

    def db_insert_device(self, device_obj):
        conn = self.conn
        cursor = conn.cursor()
        try:
            cursor.execute(
                f"INSERT INTO devices (file, reference, gateway, timer_loop, last_access, measurement) "
                f"VALUES ('{device_obj.get('file_tag')}', '{device_obj.get('reference')}', "
                f"'{device_obj.get('gateway')}', {device_obj.get('timer_loop')}, '{pendulum.now()}', "
                f"'{device_obj.get('measurement')}') "
                f"ON CONFLICT (reference) DO UPDATE SET file='{device_obj.get('file_tag')}', "
                f"gateway='{device_obj.get('gateway')}', timer_loop={device_obj.get('timer_loop')}, "
                f"last_access='{pendulum.now()}', measurement='{device_obj.get('measurement')}' "
                f"RETURNING device_id;"
            )

        except (Exception, psycopg2.Error) as error:
            print(error.pgerror)
        conn.commit()

    def db_insert_channels(self, data_channels):
        conn = self.conn
        cursor = conn.cursor()
        cursor.execute(f"SELECT device_id FROM devices WHERE reference='{data_channels.get('reference')}' "
                       f"AND file='{data_channels.get('file_tag')}';")
        device_id = cursor.fetchone()[0]
        for channel in data_channels.get('channels'):
            # Comentario si la columna writable existe
            # query = (
            #     f"INSERT INTO channels (device_id, channel, unit, item, writable) "
            #     f"SELECT '{device_id}', {get_value_in_list_channel(channel.get('virtual_channel'))}, "
            #     f"'{channel.get('unit')}', '{channel.get('item')}', {channel.get('writable')} "
            #     f"WHERE NOT EXISTS (SELECT device_id FROM channels WHERE "
            #     f"device_id='{device_id}' AND channel='{channel.get('virtual_channel')}') "
            #     f"RETURNING channel_id;"
            # )
            query = (
                f"INSERT INTO channels (device_id, channel, unit, item) "
                f"SELECT '{device_id}', {get_value_in_list_channel(channel.get('virtual_channel'))}, "
                f"'{channel.get('unit')}', '{channel.get('item')}' "
                f"WHERE NOT EXISTS (SELECT device_id FROM channels WHERE "
                f"device_id='{device_id}' AND channel='{channel.get('virtual_channel')}') "
                f"RETURNING channel_id;"
            )
            try:
                cursor.execute(query)
                conn.commit()
                try:
                    cursor.fetchone()[0]
                except TypeError:
                    # Comentario si la columna writable existe
                    # query = (
                    #     f"UPDATE channels SET (unit, item, writable) = "
                    #     f"('{channel.get('unit')}', '{channel.get('item')}', {channel.get('writable')}) "
                    #     f"WHERE device_id='{device_id}' AND channel='{channel.get('virtual_channel')}' "
                    #     f"RETURNING channel_id;"
                    # )
                    query = (
                        f"UPDATE channels SET (unit, item) = "
                        f"('{channel.get('unit')}', '{channel.get('item')}') "
                        f"WHERE device_id='{device_id}' AND channel='{channel.get('virtual_channel')}' "
                        f"RETURNING channel_id;"
                    )
                    cursor.execute(query)
                    conn.commit()

            except errors.UndefinedTable as e:
                print(e)

