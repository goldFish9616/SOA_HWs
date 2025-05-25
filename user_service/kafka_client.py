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
    "registration": "user_registration"
}


def send_event(topic, event_type, data: dict):
    payload = {
        "type": event_type,
        "timestamp": datetime.utcnow().isoformat(),
        "data": data
    }
    producer.send(topic, value=payload)
    producer.flush()


def send_registration_event(user_id: int):
    data = {"user_id": user_id, "timestamp": datetime.utcnow().isoformat()}
    send_event(TOPICS["registration"], "registration", data)


