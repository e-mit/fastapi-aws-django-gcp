"""Tests for message.py"""
from datetime import datetime, timezone
import time

from fastapi.testclient import TestClient

from function.app.routers import message

client = TestClient(message.router)


def timestamp_is_recent(timestamp_ms: int,
                        max_timedelta_s: float = 1.0) -> bool:
    """Is timestamp within max_timedelta_s seconds of now?"""
    time_diff = abs((timestamp_ms/1000) - datetime.now().timestamp())
    return time_diff < max_timedelta_s


def test_create_stored_message():
    msg = message.InputMessage(name="me", text="Test text")
    stored_msg = message.StoredMessage.create(msg)
    stored_msg2 = message.StoredMessage.create(msg)
    assert msg.name == stored_msg.name
    assert msg.text == stored_msg.text
    assert stored_msg.id != stored_msg2.id
    assert timestamp_is_recent(stored_msg.timestamp_ms)


def test_post_message():
    response = client.post("/", json={"name": "Bob", "text": "Hello"})
    assert response.status_code == 201
    msg = response.json()
    assert msg['text'] == "Hello"
    assert timestamp_is_recent(msg['timestamp_ms'])


def test_get_message_by_id():
    TEST_ID = "12345"
    response = client.get(f"/{TEST_ID}")
    assert response.status_code == 200
    assert response.json() is None
    msg = message.StoredMessage.create(
        message.InputMessage(name="my name", text="Test text"))
    msg.id = TEST_ID
    msg.post()
    response = client.get(f"/{TEST_ID}")
    assert response.status_code == 200
    data = response.json()
    assert timestamp_is_recent(data['timestamp_ms'])
    for field in ['name', 'text', 'id']:
        assert data[field] == getattr(msg, field)


def test_get_messages():
    ts_now = int(datetime.now().timestamp()*1000)
    response = client.get(
        f"?before_timestamp_ms={ts_now}&limit={message.MAX_PAGE_SIZE}")
    assert response.status_code == 200
    start_qty = len(response.json())

    msg1 = message.StoredMessage.create(
        message.InputMessage(name="me", text="Test text"))
    msg1.post()
    time.sleep(4)
    msg2 = message.StoredMessage.create(
        message.InputMessage(name="John Smith", text="This is a test."))
    msg2.post()
    ts_now = int(datetime.now().timestamp()*1000)
    response = client.get(
        f"?before_timestamp_ms={ts_now}&limit={message.MAX_PAGE_SIZE}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == (start_qty + 2)
    assert data[0]['id'] != data[1]['id']
    assert data[0]['timestamp_ms'] != data[1]['timestamp_ms']
    assert timestamp_is_recent(data[0]['timestamp_ms'])
    assert timestamp_is_recent(data[1]['timestamp_ms'], 5)
    for field in ['name', 'text', 'id']:
        # Item 0 should be most recent:
        assert data[0][field] == getattr(msg2, field)
        assert data[1][field] == getattr(msg1, field)


def db_contains_id(id: str) -> bool:
    response = client.get(f"/{id}")
    assert response.status_code == 200
    return response.json() is not None


def test_delete_message():
    msg = message.StoredMessage.create(
        message.InputMessage(name="me", text="Hello text"))
    msg.post()
    assert db_contains_id(msg.id)
    response = client.delete(f"/{msg.id}")
    assert response.status_code == 204
    assert not db_contains_id(msg.id)
