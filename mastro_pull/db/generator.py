# -*- coding: utf-8 -*-
from rich.console import Console
from rich.table import Table

from core.config import Settings
config: Settings = Settings()

def grafana_generator(pg_client) -> None:

    table = Table()
    table.add_column("File", style="magenta")
    table.add_column("Device", justify="right", style="cyan", no_wrap=True)
    table.add_column("Channel", justify="right", style="yellow", no_wrap=True)
    table.add_column("Query", justify="left", style="green")

    query = (
        "SELECT channel_id, item, reference, measurement, file "
        "FROM channels ch INNER JOIN devices d ON ch.device_id = d.device_id;"
    )
    try:
        conn = pg_client.conn
        cursor = conn.cursor()
        cursor.execute(query)

        for record in cursor:
            table.add_row(
                record[4],
                record[2],
                record[1],
                f"SELECT time, data_value AS \"{record[1]}\" "
                f"FROM data_{config.measurement} dt WHERE dt.channel_id = '{record[0]}'"
            )

        console = Console()
        console.print(table)

    except Exception as e:
        print(e)
