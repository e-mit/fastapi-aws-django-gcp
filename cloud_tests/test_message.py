"""Tests for message.py"""
import os

import requests

from function.app.main import MESSAGE_PREFIX
from tests.test_message import timestamp_is_recent

CLOUD_URL = os.environ['CLOUD_URL']


def test_post_and_delete_message():
    test_message = {"name": "Test name", "text": "Hello this is a test."}
    response = requests.post(os.path.join(CLOUD_URL, MESSAGE_PREFIX),
                             json=test_message)
    assert response.status_code == 201
    msg = response.json()
    assert msg['name'] == test_message['name']
    assert msg['text'] == test_message['text']
    assert timestamp_is_recent(msg['timestamp_ms'])
    assert isinstance(msg['id'], str)
    response = requests.delete(os.path.join(CLOUD_URL,
                                            MESSAGE_PREFIX, str(msg['id'])))
    assert response.status_code == 204
    assert len(response.text) == 0
