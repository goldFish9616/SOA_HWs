from kafka import KafkaProducer
import json
from datetime import datetime
import os

KAFKA_HOST = os.getenv("KAFKA_HOST", "kafka")
KAFKA_PORT = os.getenv("KAFKA_PORT", "29092")

producer = KafkaProducer(
    bootstrap_servers=f'{KAFKA_HOST}:{KAFKA_PORT}',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

TOPICS = {
    "view": "promocode_views",
    "click": "promocode_clicks",
    "like": "promocode_likes",
    "comment": "promocode_comments"
}


def send_event(topic, event_type, data: dict):
    payload = {
        "type": event_type,
        "timestamp": datetime.utcnow().isoformat(),
        "data": data
    }
    producer.send(topic, value=payload)
    producer.flush()


def send_view_event(user_id: int, promocode_id: int):
    data = {"user_id": user_id, "promocode_id": promocode_id, "timestamp": datetime.utcnow().isoformat()}
    send_event(TOPICS["view"], "view", data)


def send_click_event(user_id: int, promocode_id: int):
    data = {"user_id": user_id, "promocode_id": promocode_id, "timestamp": datetime.utcnow().isoformat()}
    send_event(TOPICS["click"], "click", data)


def send_like_event(user_id: int, promocode_id: int):
    data = {"user_id": user_id, "promocode_id": promocode_id, "timestamp": datetime.utcnow().isoformat()}
    send_event(TOPICS["like"], "like", data)


def send_comment_event(user_id: int, promocode_id: int, comment: str):
    data = {"user_id": user_id, "promocode_id": promocode_id, "comment": comment, "timestamp": datetime.utcnow().isoformat()}
    send_event(TOPICS["comment"], "comment", data)

