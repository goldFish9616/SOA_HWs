def test_kafka_view_event_consumed_and_saved(kafka_producer, test_db):
    kafka_producer.send("views", {"promo_id": 10, "user_id": 1})
    wait_for_kafka()
    result = test_db.query(View).filter_by(promo_id=10).first()
    assert result is not None

def test_kafka_like_event_saved(kafka_producer, test_db):
    kafka_producer.send("like", {"promo_id": 5})
    wait_for_kafka()
    result = test_db.query(Like).filter_by(promo_id=5).first()
    assert result is not None
