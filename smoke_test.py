import requests
import json
import time

BASE_URL = 'http://localhost:8000/api'

# Ensure the server is up
for _ in range(5):
    try:
        requests.get(BASE_URL)
        break
    except:
        time.sleep(1)

def print_json(data):
    print(json.dumps(data, indent=2))

print("=== a. Register user ===")
register_res = requests.post(f"{BASE_URL}/auth/register/", json={
    "username": "testuser_smoke",
    "email": "smoke@example.com",
    "password": "smokepassword123"
})
print(register_res.status_code)
print_json(register_res.json())

print("\n=== b. Login ===")
login_res = requests.post(f"{BASE_URL}/auth/login/", json={
    "username": "testuser_smoke",
    "password": "smokepassword123"
})
token = login_res.json().get('access')
headers = {'Authorization': f'Bearer {token}'}

print("\n=== c. Create Category ===")
cat_res = requests.post(f"{BASE_URL}/categories/", json={"name": "Groceries"}, headers=headers)
cat_id = cat_res.json()['id']
print_json(cat_res.json())

print("\n=== d. Create 4 normal transactions ===")
for amount in [500, 600, 700, 800]:
    res = requests.post(f"{BASE_URL}/transactions/", json={
        "category": cat_id,
        "amount": amount,
        "type": "expense",
        "date": "2023-10-01",
        "description": f"Normal {amount}"
    }, headers=headers)
    print(f"Status: {res.status_code}, amount: {amount}, is_anomaly: {res.json().get('is_anomaly')}")

print("\n=== e. Create 5th transaction at 3x average (anomaly) ===")
# Average is 650. 3x is 1950.
anomaly_res = requests.post(f"{BASE_URL}/transactions/", json={
    "category": cat_id,
    "amount": 2500,
    "type": "expense",
    "date": "2023-10-02",
    "description": "Anomaly transaction"
}, headers=headers)
print_json(anomaly_res.json())

print("\n=== f. Create brand-new category and cold-start anomaly ===")
cat2_res = requests.post(f"{BASE_URL}/categories/", json={"name": "Electronics"}, headers=headers)
cat2_id = cat2_res.json()['id']

cold_start_res = requests.post(f"{BASE_URL}/transactions/", json={
    "category": cat2_id,
    "amount": 6000,
    "type": "expense",
    "date": "2023-10-03",
    "description": "Cold start anomaly"
}, headers=headers)
print_json(cold_start_res.json())
