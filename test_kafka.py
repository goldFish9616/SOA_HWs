from kafka import KafkaProducer
import json
from datetime import datetime

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def send_registration_event(client_id: int):
    event = {
        "client_id": client_id,
        "registered_at": datetime.utcnow().isoformat() + "Z"
    }
    producer.send('client_registration', event)
    producer.flush()

def send_interaction_event(client_id: int, entity_type: str, entity_id: int, event_type: str):
    event = {
        "client_id": client_id,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "event_type": event_type,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    producer.send('interaction_events', event)
    producer.flush()

def send_view_event(client_id: int, entity_type: str, entity_id: int):
    event = {
        "client_id": client_id,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "event_type": "view",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    producer.send('view_events', event)
    producer.flush()

def send_comment_event(client_id: int, entity_type: str, entity_id: int, comment: str):
    event = {
        "client_id": client_id,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "comment_text": comment,
        "event_type": "comment",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    producer.send('comment_events', event)
    producer.flush()
