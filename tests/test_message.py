"""Tests for message.py"""
from datetime import datetime, timezone, timedelta
import dateutil.parser
import time

from fastapi.testclient import TestClient

from function.app.routers import message

client = TestClient(message.router)


def timestamp_is_recent(timestamp: str, max_timedelta_s: float = 1.0) -> bool:
    """Is timestamp within max_timedelta_s seconds of now?"""
    time_diff = abs(dateutil.parser.isoparse(timestamp)
                    - datetime.now(tz=timezone.utc))
    return time_diff < timedelta(seconds=max_timedelta_s)


def test_create_stored_message():
    msg = message.InputMessage(name="me", text="Test text")
    stored_msg = message.StoredMessage.create(msg)
    stored_msg2 = message.StoredMessage.create(msg)
    assert msg.name == stored_msg.name
    assert msg.text == stored_msg.text
    assert stored_msg.id != stored_msg2.id
    assert timestamp_is_recent(str(stored_msg.timestamp))


def test_post_message():
    response = client.post("/", json={"name": "Bob", "text": "Hello"})
    assert response.status_code == 201
    msg = response.json()
    assert msg['text'] == "Hello"
    assert timestamp_is_recent(msg['timestamp'])


def test_get_message():
    response = client.get("/")
    assert response.status_code == 200
    start_qty = len(response.json())

    msg1 = message.StoredMessage.create(
        message.InputMessage(name="me", text="Test text"))
    msg1.post()
    time.sleep(4)
    msg2 = message.StoredMessage.create(
        message.InputMessage(name="John Smith", text="This is a test."))
    msg2.post()
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == (start_qty + 2)
    assert data[0]['id'] != data[1]['id']
    assert data[0]['timestamp'] != data[1]['timestamp']
    assert timestamp_is_recent(data[0]['timestamp'])
    assert timestamp_is_recent(data[1]['timestamp'], 5)
    for field in ['name', 'text', 'id']:
        # Item 0 should be most recent:
        assert data[0][field] == getattr(msg2, field)
        assert data[1][field] == getattr(msg1, field)


def db_contains_id(id: str):
    response = client.get("/")
    assert response.status_code == 200
    all_data = response.json()
    found_id = False
    for data in all_data:
        found_id = found_id or (data['id'] == id)
    return found_id


def test_delete_message():
    msg = message.StoredMessage.create(
        message.InputMessage(name="me", text="Hello text"))
    msg.post()

    assert db_contains_id(msg.id)

    response = client.delete(f"/{msg.id}")
    assert response.status_code == 200

    assert not db_contains_id(msg.id)
