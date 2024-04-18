"""Tests for message.py"""
from datetime import datetime, timezone, timedelta
import dateutil.parser

from fastapi.testclient import TestClient

from function.routers import message

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
    msg1 = message.StoredMessage.create(
        message.InputMessage(name="me", text="Test text"))
    msg2 = message.StoredMessage.create(
        message.InputMessage(name="John Smith", text="This is a test."))
    message.messages = [msg1, msg2]
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]['id'] != data[1]['id']
    assert data[0]['timestamp'] != data[1]['timestamp']
    assert timestamp_is_recent(data[0]['timestamp'])
    assert timestamp_is_recent(data[1]['timestamp'])
    for field in ['name', 'text']:
        assert data[0][field] == getattr(msg1, field)
        assert data[1][field] == getattr(msg2, field)
