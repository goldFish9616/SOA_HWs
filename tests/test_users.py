def test_register_user(client):
    response = client.post("/register", json={"login": "alice", "password": "1234"})
    assert response.status_code == 200
    assert "user_id" in response.json()

def test_login_user(client):
    client.post("/register", json={"login": "bob", "password": "5678"})
    response = client.post("/login", json={"login": "bob", "password": "5678"})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_duplicate_registration(client):
    client.post("/register", json={"login": "charlie", "password": "pass"})
    response = client.post("/register", json={"login": "charlie", "password": "pass"})
    assert response.status_code == 400
