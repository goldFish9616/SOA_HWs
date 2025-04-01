import pytest
from user_service import app as user_app, db as user_db
from promocodes.promocode_service import app as promo_app, db as promo_db
from flask_jwt_extended import create_access_token

@pytest.fixture
def client():
    user_app.config['TESTING'] = True
    user_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    promo_app.config['TESTING'] = True
    promo_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with user_app.test_client() as user_client, promo_app.test_client() as promo_client:
        with user_app.app_context():
            user_db.create_all()
        with promo_app.app_context():
            promo_db.create_all()
        yield user_client, promo_client

# Тест регистрации пользователя
def test_register_user(client):
    user_client, _ = client
    response = user_client.post('/register', json={
        'username': 'testuser',
        'password': 'testpass'
    })
    assert response.status_code == 201
    assert response.json['message'] == 'User registered successfully'

# Тест авторизации
def test_login_user(client):
    user_client, _ = client
    user_client.post('/register', json={
        'username': 'testuser',
        'password': 'testpass'
    })
    response = user_client.post('/login', json={
        'username': 'testuser',
        'password': 'testpass'
    })
    assert response.status_code == 200
    assert 'access_token' in response.json

# Тест создания промокода
def test_create_promocode(client):
    _, promo_client = client
    token = create_access_token(identity='admin')
    response = promo_client.post('/promocode', json={
        'code': 'DISCOUNT10',
        'discount': 10
    }, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 201
    assert response.json['message'] == 'Promocode created'

# Тест получения списка промокодов
def test_get_promocodes(client):
    _, promo_client = client
    response = promo_client.get('/promocode')
    assert response.status_code == 200
    assert isinstance(response.json, list)
