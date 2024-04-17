"""Tests for main.py"""
from fastapi.testclient import TestClient

from app import main

client = TestClient(main.app)


def test_get_hello():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello"}


def test_get_version():
    response = client.get("/version")
    assert response.status_code == 200
    assert response.json() == {"api_version": main.VERSION}
