"""Tests for users.py"""
from fastapi.testclient import TestClient

from function.app.routers import users

client = TestClient(users.router)


def test_read_users():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello users"}
