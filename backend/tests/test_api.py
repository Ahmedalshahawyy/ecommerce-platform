import os
import json
from fastapi.testclient import TestClient
from backend.main import app

CLIENT = TestClient(app)
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'ecommerce.db')


def setup_module(module):
    # Reset DB to ensure clean state (drop & recreate tables)
    from backend.db import engine, Base

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_health():
    r = CLIENT.get('/health')
    assert r.status_code == 200
    assert r.json().get('status') == 'ok'


def test_register_login_and_product_and_cart():
    # register
    r = CLIENT.post('/auth/register', json={'username': 'tester', 'password': 'secret'})
    assert r.status_code in (200,201)

    # login
    data = {'username': 'tester', 'password': 'secret'}
    r = CLIENT.post('/auth/login', data=data)
    assert r.status_code == 200
    token = r.json()['access_token']
    assert token

    headers = {'Authorization': f'Bearer {token}'}

    # create product
    prod = {'name': 'Widget', 'price': 9.99, 'description': 'A widget'}
    r = CLIENT.post('/products', json=prod)
    assert r.status_code == 200
    pid = r.json()['id']

    # list products
    r = CLIENT.get('/products')
    assert r.status_code == 200
    items = r.json()
    assert any(it['name'] == 'Widget' for it in items)

    # add to cart
    r = CLIENT.post('/cart/add', json={'product_id': pid, 'quantity': 2}, headers=headers)
    assert r.status_code == 200

    # get cart
    r = CLIENT.get('/cart', headers=headers)
    assert r.status_code == 200
    c = r.json()
    assert len(c) == 1
    assert c[0]['quantity'] == 2


def test_update_and_delete_product():
    # create user and login
    r = CLIENT.post('/auth/register', json={'username': 'updater', 'password': 'secret'})
    assert r.status_code in (200, 201)
    data = {'username': 'updater', 'password': 'secret'}
    r = CLIENT.post('/auth/login', data=data)
    token = r.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # create product
    prod = {'name': 'Gadget', 'price': 19.99, 'description': 'A gadget'}
    r = CLIENT.post('/products', json=prod)
    assert r.status_code == 200
    pid = r.json()['id']

    # update product
    updated = {'name': 'Gadget Pro', 'price': 29.99, 'description': 'Upgraded gadget'}
    r = CLIENT.put(f'/products/{pid}', json=updated, headers=headers)
    assert r.status_code == 200
    assert r.json()['name'] == 'Gadget Pro'

    # delete product
    r = CLIENT.delete(f'/products/{pid}', headers=headers)
    assert r.status_code == 200

    # get should now 404
    r = CLIENT.get(f'/products/{pid}')
    assert r.status_code == 404


def test_expired_token():
    # ensure user exists
    r = CLIENT.post('/auth/register', json={'username': 'expuser', 'password': 'secret'})
    assert r.status_code in (200, 201)

    # create an expired token manually
    from datetime import datetime, timedelta, timezone
    from backend.main import SECRET_KEY, ALGORITHM
    from jose import jwt as pyjwt

    past = int((datetime.now(timezone.utc) - timedelta(seconds=10)).timestamp())
    token = pyjwt.encode({'sub': 'expuser', 'exp': past}, SECRET_KEY, algorithm=ALGORITHM)

    headers = {'Authorization': f'Bearer {token}'}
    r = CLIENT.get('/cart', headers=headers)
    assert r.status_code == 401
