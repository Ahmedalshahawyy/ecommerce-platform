import os
import requests
import time

BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')
MAX_RETRIES = 30
RETRY_INTERVAL = 1

def wait_for_api():
    """Wait for API to be ready."""
    for _ in range(MAX_RETRIES):
        try:
            r = requests.get(f'{BASE_URL}/health')
            if r.status_code == 200:
                return
        except Exception:
            pass
        time.sleep(RETRY_INTERVAL)
    raise RuntimeError(f"API not ready after {MAX_RETRIES * RETRY_INTERVAL} seconds")

def test_e2e_flow():
    """End-to-end flow: register, login, create product, add to cart."""
    wait_for_api()
    
    # Register
    r = requests.post(f'{BASE_URL}/auth/register', json={'username': 'e2e_user', 'password': 'e2e_pass'})
    assert r.status_code in (200, 201)
    
    # Login
    r = requests.post(f'{BASE_URL}/auth/login', data={'username': 'e2e_user', 'password': 'e2e_pass'})
    assert r.status_code == 200
    token = r.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    
    # Create product
    r = requests.post(f'{BASE_URL}/products', json={'name': 'E2E Test Item', 'price': 19.99})
    assert r.status_code == 200
    pid = r.json()['id']
    
    # Update product
    r = requests.put(f'{BASE_URL}/products/{pid}', json={'name': 'E2E Test Item Updated', 'price': 29.99, 'description': 'updated'}, headers=headers)
    assert r.status_code == 200
    assert r.json()['name'] == 'E2E Test Item Updated'

    # Delete product
    r = requests.delete(f'{BASE_URL}/products/{pid}', headers=headers)
    assert r.status_code == 200
    
    # Add to cart
    r = requests.post(f'{BASE_URL}/cart/add', json={'product_id': pid, 'quantity': 1}, headers=headers)
    assert r.status_code == 200
    
    # Get cart
    r = requests.get(f'{BASE_URL}/cart', headers=headers)
    assert r.status_code == 200
    cart = r.json()
    assert len(cart) > 0
    assert cart[0]['product_id'] == pid
