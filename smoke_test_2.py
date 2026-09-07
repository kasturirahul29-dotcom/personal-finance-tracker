import requests
import json
import time

BASE_URL = 'http://localhost:8000/api'

def print_json(data):
    print(json.dumps(data, indent=2))

print("=== 1. Setup new user ===")
register_res = requests.post(f"{BASE_URL}/auth/register/", json={
    "username": "testuser_smoke3",
    "email": "smoke3@example.com",
    "password": "smokepassword123"
})
login_res = requests.post(f"{BASE_URL}/auth/login/", json={
    "username": "testuser_smoke3",
    "password": "smokepassword123"
})
token = login_res.json().get('access')
headers = {'Authorization': f'Bearer {token}'}

cat_res = requests.post(f"{BASE_URL}/categories/", json={"name": "Groceries2"}, headers=headers)
cat_id = cat_res.json()['id']
print(f"Created category ID: {cat_id}")

print("\n=== 1a. Create a budget ===")
budget_payload = {"category": cat_id, "monthly_limit": 2000, "month": "2026-09-01"}
b_res = requests.post(f"{BASE_URL}/budgets/", json=budget_payload, headers=headers)
print_json(b_res.json())

print("\n=== 1b. Duplicate budget ===")
dup_res = requests.post(f"{BASE_URL}/budgets/", json=budget_payload, headers=headers)
print(f"Status: {dup_res.status_code}")
print_json(dup_res.json())

print("\n=== Setup 3 months of history for suggestions ===")
for month in [6, 7, 8]:
    requests.post(f"{BASE_URL}/transactions/", json={
        "category": cat_id, "amount": 1000, "type": "expense", 
        "date": f"2026-0{month}-15", "description": f"Month {month}"
    }, headers=headers)

print("\n=== 1c. Suggestion endpoint ===")
sug_res = requests.get(f"{BASE_URL}/budgets/suggestions/?category={cat_id}", headers=headers)
print_json(sug_res.json())

print("\n=== 1d. Exceed 80% (approaching_limit) ===")
# Budget is 2000. 80% is 1600.
requests.post(f"{BASE_URL}/transactions/", json={
    "category": cat_id, "amount": 1700, "type": "expense", 
    "date": "2026-09-10", "description": "Big spend"
}, headers=headers)
sug_res_80 = requests.get(f"{BASE_URL}/budgets/suggestions/?category={cat_id}", headers=headers)
print_json(sug_res_80.json())

print("\n=== 1e. Exceed 100% (over_budget) ===")
requests.post(f"{BASE_URL}/transactions/", json={
    "category": cat_id, "amount": 400, "type": "expense", 
    "date": "2026-09-11", "description": "Overspend"
}, headers=headers)
sug_res_100 = requests.get(f"{BASE_URL}/budgets/suggestions/?category={cat_id}", headers=headers)
print_json(sug_res_100.json())

print("\n=== 2a. Dashboard summary ===")
dash_res = requests.get(f"{BASE_URL}/dashboard/summary/?month=2026-09-01", headers=headers)
print_json(dash_res.json())

print("\n=== 2b. Dashboard predict (Linear Regression, 4 months data) ===")
# We have months 6, 7, 8, 9 now (4 months)
pred_res = requests.get(f"{BASE_URL}/dashboard/predict/?category={cat_id}", headers=headers)
print_json(pred_res.json())

print("\n=== 2c. Predict for zero transactions ===")
cat_zero_res = requests.post(f"{BASE_URL}/categories/", json={"name": "ZeroCat"}, headers=headers)
cat_zero_id = cat_zero_res.json()['id']
pred_zero_res = requests.get(f"{BASE_URL}/dashboard/predict/?category={cat_zero_id}", headers=headers)
print(f"Status: {pred_zero_res.status_code}")
print_json(pred_zero_res.json())
