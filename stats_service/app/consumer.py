# app/consumer.py
from kafka import KafkaConsumer
from clickhouse_driver import Client
import json
import os
from datetime import datetime

KAFKA_HOST = os.getenv("KAFKA_HOST", "kafka")
KAFKA_PORT = os.getenv("KAFKA_PORT", "29092")

TOPICS = ["promocode_views", "promocode_clicks", "promocode_likes", "promocode_comments"]

TYPE_MAP = {
    "promocode_views": "view",
    "promocode_clicks": "click",
    "promocode_likes": "like",
    "promocode_comments": "comment",
}

def start_consumer():
    client = Client(host=os.getenv("CLICKHOUSE_HOST", "clickhouse"))
    consumer = KafkaConsumer(
        *TOPICS,
        bootstrap_servers=f"{KAFKA_HOST}:{KAFKA_PORT}",
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="stat_service"
    )

    for message in consumer:
        topic = message.topic
        data = message.value
        print(f"Received: {data} from {topic}")

        client.execute(
            "INSERT INTO promocode_events (user_id, promocode_id, type, comment, timestamp) VALUES",
            [(
                data["user_id"],
                data["promocode_id"],
                TYPE_MAP[topic],
                data.get("comment", ""),
                datetime.fromisoformat(data["timestamp"])
            )]
        )

