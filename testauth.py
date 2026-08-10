import requests
import json

BASE_URL = "http://127.0.0.1:8000"
session = requests.Session()

print("=" * 60)
print("1. Testing POST /auth/register")
print("=" * 60)
response = requests.post(
    f"{BASE_URL}/auth/register",
    json={"email": "thisisme@forexample.com", "password": "abcd123"}
)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
print(f"Cookies: {response.cookies}")

print("\n" + "=" * 60)
print("2. Testing POST /auth/login")
print("=" * 60)
response = session.post(
    f"{BASE_URL}/auth/login",
    json={"email": "megaian@forexample.com", "password": "abcdjwj123"}
)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
print(f"Cookies received: {session.cookies}")
access_token = response.json()["access_token"]

print("\n" + "=" * 60)
print("3. Testing GET /auth/me (protected route)")
print("=" * 60)
response = session.get(
    f"{BASE_URL}/auth/me",
    headers={"Authorization": f"Bearer {access_token}"}
)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

print("\n" + "=" * 60)
print("4. Testing POST /auth/refresh (with cookie)")
print("=" * 60)
response = session.post(f"{BASE_URL}/auth/refresh")
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
new_access_token = response.json()["access_token"]

print("\n" + "=" * 60)
print("5. Testing GET /auth/me with NEW token")
print("=" * 60)
response = session.get(
    f"{BASE_URL}/auth/me",
    headers={"Authorization": f"Bearer {new_access_token}"}
)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

print("\n" + "=" * 60)
print("6. Testing POST /auth/logout")
print("=" * 60)
response = session.post(f"{BASE_URL}/auth/logout")
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

print("\n" + "=" * 60)
print("7. Testing refresh AFTER logout (should fail)")
print("=" * 60)
response = session.post(f"{BASE_URL}/auth/refresh")
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

print("\n All tests completed!")
