from clickhouse_driver import Client
import os

def get_client():
    return Client(host=os.getenv("CLICKHOUSE_HOST", "clickhouse"))
