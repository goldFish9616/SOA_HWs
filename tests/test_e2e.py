def test_full_flow_register_create_promo_view_stats(client, promos_service, stats_service):
    client.post("/register", json={"username": "e2e_user", "password": "pass"})

    request = CreatePromoRequest(name="E2E Promo", code="E2E10", discount=10)
    promos_service.CreatePromo(request, None)

    kafka_producer.send("views", {"promo_id": 1, "user_id": 1})
    wait_for_kafka()

    response = stats_service.GetTotalViews(TotalViewsRequest(promo_id=1), None)
    assert response.count >= 1

def test_multiple_users_create_promos_and_clicks(promos_service, stats_service):
    for i in range(3):
        request = CreatePromoRequest(name=f"Promo{i}", code=f"CODE{i}", discount=5)
        promos_service.CreatePromo(request, None)
        kafka_producer.send("clicks", {"promo_id": i+1})
    wait_for_kafka()
    response = stats_service.GetClickStats(ClickStatsRequest(date="2025-06-01"), None)
    assert response.count >= 3

def test_register_and_login_flow(client):
    client.post("/register", json={"username": "flow_user", "password": "flowpass"})
    response = client.post("/login", json={"username": "flow_user", "password": "flowpass"})
    assert "access_token" in response.json()
