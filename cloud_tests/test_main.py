"""Tests which call / on the cloud API."""
import os

import requests

from fastapi_lambda.app import main

CLOUD_URL = os.environ['CLOUD_URL']


def test_get_root():
    response = requests.get(CLOUD_URL)
    assert response.status_code == 200
    assert main.TITLE in response.text


def test_get_version():
    response = requests.get(os.path.join(CLOUD_URL, "version"))
    assert response.status_code == 200
    assert response.json() == {"api_version": main.APIVersion().api_version}
