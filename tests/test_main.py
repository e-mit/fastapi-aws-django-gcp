"""Tests for main.py"""
from fastapi.testclient import TestClient

from fastapi_lambda.app import main

client = TestClient(main.app)


def test_get_root():
    response = client.get("/")
    assert response.status_code == 200
    assert main.TITLE in response.text


def test_get_version():
    response = client.get("/version")
    assert response.status_code == 200
    assert response.json() == {"api_version": main.APIVersion().api_version}
