"""Tests which call /message/ on the cloud API."""

import os
import time
from typing import Any
from pathlib import Path

import requests

from function.app.main import MESSAGE_URL_PREFIX
from tests.test_message import timestamp_is_recent

CLOUD_URL = os.environ['CLOUD_URL']
TEST_MSG_QTY = 8


def test_post_and_delete_message():
    test_message = {"name": "Test name", "subject": "test",
                    "text": "Hello this is a test."}
    response = requests.post(os.path.join(CLOUD_URL, MESSAGE_URL_PREFIX),
                             json=test_message)
    assert response.status_code == 201
    msg = response.json()
    assert msg['name'] == test_message['name']
    assert msg['text'] == test_message['text']
    assert msg['subject'] == test_message['subject']
    assert timestamp_is_recent(msg['timestamp_ms'])
    assert isinstance(msg['id'], str)
    response = requests.delete(
        os.path.join(CLOUD_URL, MESSAGE_URL_PREFIX, str(msg['id'])))
    assert response.status_code == 204
    assert len(response.text) == 0


def test_post_get_delete_message():
    test_message = {"name": "Test name2", "subject": "test2",
                    "text": "Hi this is a test."}
    response = requests.post(os.path.join(CLOUD_URL, MESSAGE_URL_PREFIX),
                             json=test_message)
    assert response.status_code == 201
    msg = response.json()
    assert msg['name'] == test_message['name']
    assert msg['text'] == test_message['text']
    assert msg['subject'] == test_message['subject']
    assert timestamp_is_recent(msg['timestamp_ms'])
    assert isinstance(msg['id'], str)
    response = requests.get(os.path.join(CLOUD_URL,
                                         MESSAGE_URL_PREFIX, str(msg['id'])))
    assert response.status_code == 200
    assert response.json() == msg
    response = requests.delete(os.path.join(CLOUD_URL,
                                            MESSAGE_URL_PREFIX, str(msg['id'])))
    assert response.status_code == 204
    assert len(response.text) == 0


def test_get_nonexistent_message_by_id():
    TEST_ID = "12345"
    response = requests.get(
        os.path.join(CLOUD_URL, MESSAGE_URL_PREFIX, TEST_ID))
    assert response.status_code == 404


def post_multiple_messages(number: int) -> list[dict[str, Any]]:
    data = []
    for n in range(0, number):
        response = requests.post(
            os.path.join(CLOUD_URL, MESSAGE_URL_PREFIX),
            json={"name": f"msg{n}", "subject": f"subject{n}",
                  "text": f"Test text {n}"})
        assert response.status_code == 201
        data.append(response.json())
        time.sleep(1)
    # Sort data newest to oldest
    return data[::-1]


def test_get_query():
    data = post_multiple_messages(TEST_MSG_QTY)

    # Test limit:
    response = requests.get(os.path.join(CLOUD_URL,
                                         MESSAGE_URL_PREFIX,
                                         "?limit=2"))
    assert response.status_code == 200
    assert response.json() == data[0:2]

    # No query params:
    response = requests.get(os.path.join(CLOUD_URL, MESSAGE_URL_PREFIX))
    assert response.status_code == 200
    assert response.json()[0:TEST_MSG_QTY] == data

    # Timestamp equal to a message; no ID
    response = requests.get(os.path.join(
        CLOUD_URL, MESSAGE_URL_PREFIX, f"?timestamp_ms={data[4]['timestamp_ms']}"))
    assert response.status_code == 200
    assert response.json()[0:(TEST_MSG_QTY - 4)] == data[4:]

    # Timestamp equal to a message, ID equal to a message
    response = requests.get(os.path.join(
        CLOUD_URL, MESSAGE_URL_PREFIX,
        f"?timestamp_ms={data[4]['timestamp_ms']}&before_id={data[4]['id']}"))
    assert response.status_code == 200
    assert response.json()[0:(TEST_MSG_QTY - 5)] == data[5:]

    for n in range(0, TEST_MSG_QTY):
        response = requests.delete(os.path.join(CLOUD_URL,
                                                MESSAGE_URL_PREFIX,
                                                str(data[n]['id'])))
        assert response.status_code == 204
        time.sleep(1)


def test_delete_all():
    post_multiple_messages(TEST_MSG_QTY)
    response = requests.get(os.path.join(CLOUD_URL, MESSAGE_URL_PREFIX))
    assert response.status_code == 200
    assert response.json() != []
    response = requests.delete(os.path.join(CLOUD_URL, MESSAGE_URL_PREFIX))
    assert response.status_code == 204
    response = requests.get(os.path.join(CLOUD_URL, MESSAGE_URL_PREFIX))
    assert response.status_code == 200
    assert response.json() == []


def test_post_location_header():
    test_message = {"name": "Alice", "subject": "test2",
                    "text": "Hi this is a test."}
    response = requests.post(os.path.join(CLOUD_URL, MESSAGE_URL_PREFIX),
                             json=test_message)
    assert response.status_code == 201
    msg = response.json()
    new_url = response.headers['location']
    assert Path(new_url).name == msg['id']
    response2 = requests.get(new_url)
    assert response2.status_code == 200
    msg2 = response2.json()
    assert msg2 == msg
