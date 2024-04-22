"""Tests for users.py"""
import os

import requests

from function.app.main import USERS_PREFIX

CLOUD_URL = os.environ['CLOUD_URL']


def test_read_users():
    response = requests.get(os.path.join(CLOUD_URL, USERS_PREFIX))
    assert response.status_code == 200
    assert response.json() == {"message": "Hello users"}
