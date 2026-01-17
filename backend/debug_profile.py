#!/usr/bin/env python3
"""Debug script to test the profile endpoint specifically."""

from fastapi.testclient import TestClient
from src.main import app

def test_profile_endpoint():
    client = TestClient(app)

    # Try to access the endpoint with a mock request
    response = client.put(
        "/auth/profile",
        headers={"Authorization": "Bearer fake-token", "Content-Type": "application/json"},
        json={"name": "Test User", "email": "test@example.com"}
    )

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    print(f"Response Headers: {dict(response.headers)}")

if __name__ == "__main__":
    test_profile_endpoint()