"""Tests which call / on the cloud API."""
import os

import requests

from function.app import main

CLOUD_URL = os.environ['CLOUD_URL']


def test_get_hello():
    response = requests.get(CLOUD_URL)
    assert response.status_code == 200
    assert response.json() == {"message": "Hello"}


def test_get_version():
    response = requests.get(os.path.join(CLOUD_URL, "version"))
    assert response.status_code == 200
    assert response.json() == {"api_version": main.VERSION}
