"""Tests for message.py"""
from datetime import datetime
import time
from pathlib import Path

from fastapi.testclient import TestClient
from fastapi import HTTPException
import pytest

from function.app.routers import message

client = TestClient(message.router)


def timestamp_is_recent(timestamp_ms: int,
                        max_timedelta_s: float = 1.0) -> bool:
    """Is timestamp within max_timedelta_s seconds of now?"""
    time_diff = abs((timestamp_ms/1000) - datetime.now().timestamp())
    return time_diff < max_timedelta_s


def test_create_stored_message():
    msg = message.InputMessage(name="me", subject="hello", text="Test text")
    stored_msg = message.StoredMessage.create(msg)
    stored_msg2 = message.StoredMessage.create(msg)
    assert msg.name == stored_msg.name
    assert msg.subject == stored_msg.subject
    assert msg.text == stored_msg.text
    assert stored_msg.id != stored_msg2.id
    assert timestamp_is_recent(stored_msg.timestamp_ms)


def test_post_message():
    data = {"name": "Bob", "subject": "hi", "text": "Hello"}
    response = client.post("/", json=data)
    assert response.status_code == 201
    msg = response.json()
    for k in data:
        assert msg[k] == data[k]
    assert timestamp_is_recent(msg['timestamp_ms'])


def test_post_location_header():
    data = {"name": "Alice", "subject": "hello", "text": "hi"}
    response = client.post("/", json=data)
    assert response.status_code == 201
    msg = response.json()
    new_url = response.headers['location']
    assert Path(new_url).name == msg['id']


def test_get_nonexistent_message_by_id():
    TEST_ID = "12345"
    with pytest.raises(HTTPException) as excinfo:
        client.get(f"/{TEST_ID}")
    assert excinfo.value.status_code == 404


def test_get_message_by_id():
    TEST_ID = "12345"
    msg = message.StoredMessage.create(
        message.InputMessage(name="my name", subject="the subject",
                             text="Test text"))
    msg.id = TEST_ID
    msg.post()
    response = client.get(f"/{TEST_ID}")
    assert response.status_code == 200
    data = response.json()
    assert timestamp_is_recent(data['timestamp_ms'])
    for field in ['name', 'subject', 'text', 'id']:
        assert data[field] == getattr(msg, field)


def test_get_messages():
    ts_now = int(datetime.now().timestamp()*1000)
    response = client.get(
        f"?timestamp_ms={ts_now}&limit={message.MAX_PAGE_SIZE}")
    assert response.status_code == 200
    start_qty = len(response.json())

    msg1 = message.StoredMessage.create(
        message.InputMessage(name="me", subject="subj", text="Test text"))
    msg1.post()
    time.sleep(4)
    msg2 = message.StoredMessage.create(
        message.InputMessage(name="John Smith", subject="hi",
                             text="This is a test."))
    msg2.post()
    ts_now = int(datetime.now().timestamp()*1000)
    response = client.get(
        f"?timestamp_ms={ts_now}&limit={message.MAX_PAGE_SIZE}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == (start_qty + 2)
    assert data[0]['id'] != data[1]['id']
    assert data[0]['timestamp_ms'] != data[1]['timestamp_ms']
    assert timestamp_is_recent(data[0]['timestamp_ms'])
    assert timestamp_is_recent(data[1]['timestamp_ms'], 5)
    for field in ['name', 'text', 'subject', 'id']:
        # Item 0 should be most recent:
        assert data[0][field] == getattr(msg2, field)
        assert data[1][field] == getattr(msg1, field)


def db_contains_id(id: str) -> bool:
    response = client.get(f"/{id}")
    assert response.status_code == 200
    return response.json() is not None


def test_delete_message():
    msg = message.StoredMessage.create(
        message.InputMessage(name="me", subject="subject text",
                             text="Hello text"))
    msg.post()
    assert client.get(f"/{msg.id}").status_code == 200
    response = client.delete(f"/{msg.id}")
    assert response.status_code == 204
    with pytest.raises(HTTPException) as excinfo:
        client.get(f"/{msg.id}")
    assert excinfo.value.status_code == 404


def delete_all_loop():
    future_ts = int((datetime.now().timestamp() + 1000)*1000)
    response = client.get(f"?timestamp_ms={future_ts}"
                          f"&limit={message.MAX_PAGE_SIZE}")
    assert response.status_code == 200
    data = response.json()
    for item in data:
        response = client.delete(f"/{item['id']}")
        assert response.status_code == 204
    response = client.get(f"?timestamp_ms={future_ts}"
                          f"&limit={message.MAX_PAGE_SIZE}")
    assert response.status_code == 200
    assert response.json() == []


def test_delete_all_loop():
    msg1 = message.StoredMessage.create(
        message.InputMessage(name="me", subject="hi", text="Test text"))
    msg1.post()
    time.sleep(4)
    msg2 = message.StoredMessage.create(
        message.InputMessage(name="John Smith", subject="the subject",
                             text="This is a test."))
    msg2.post()

    future_ts = int((datetime.now().timestamp() + 1000)*1000)
    response = client.get(f"?timestamp_ms={future_ts}"
                          f"&limit={message.MAX_PAGE_SIZE}")
    assert response.status_code == 200
    assert response.json() != []
    delete_all_loop()
    response = client.get(f"?timestamp_ms={future_ts}"
                          f"&limit={message.MAX_PAGE_SIZE}")
    assert response.status_code == 200
    assert response.json() == []


TIMESTEP = 10000


@pytest.fixture
def prepare_db() -> list[message.StoredMessage]:
    """Clear all messages, then add a series of new ones. Return end time."""
    delete_all_loop()
    msg_data = []

    ts_ms = int(datetime.now().timestamp()*1000)
    for n in range(0, 3):
        msg = message.StoredMessage.create(
            message.InputMessage(name=f"msg{n}", subject=f"subject{n}",
                                 text=f"Test text {n}"))
        msg.timestamp_ms = ts_ms - (TIMESTEP * n)
        msg.post()
        msg_data.append(msg)

    # Add 4 messages with same timestamp:
    for n in range(3, 7):
        msg = message.StoredMessage.create(
            message.InputMessage(name=f"msg{n}", subject=f"subj{n}",
                                 text=f"Test text {n}"))
        msg.timestamp_ms = ts_ms - (TIMESTEP * 3)
        msg.post()
        msg_data.append(msg)

    for n in range(7, 9):
        msg = message.StoredMessage.create(
            message.InputMessage(name=f"msg{n}", subject=f"subj{n}",
                                 text=f"Test text {n}"))
        msg.timestamp_ms = ts_ms - (TIMESTEP * n)
        msg.post()
        msg_data.append(msg)

    return msg_data


def test_exclude_newer(prepare_db):
    ts = int(prepare_db[0].timestamp_ms - (0.5 * TIMESTEP))
    response = client.get(f"?timestamp_ms={ts}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 8
    for item in data:
        assert item['timestamp_ms'] < ts


def test_query_without_id(prepare_db):
    """A match of timestamp without id should include that message."""
    response = client.get(f"?timestamp_ms={prepare_db[1].timestamp_ms}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 8
    ok = False
    for item in data:
        ok = ok or (item['name'] == "msg1")
    assert ok


def test_query_with_id(prepare_db):
    """A match of both timestamp and id should exclude that message."""
    response = client.get(f"?timestamp_ms={prepare_db[1].timestamp_ms}"
                          f"&before_id={prepare_db[1].id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 7
    ok = True
    for item in data:
        ok = ok and (item['name'] != "msg1")
    assert ok


def test_query_with_id_no_time(prepare_db):
    """A match of id but no timestamp should select all."""
    response = client.get(f"?before_id={prepare_db[1].id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 9


def test_query_blank(prepare_db):
    """No query params should select all."""
    response = client.get("")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 9


def test_pagination(prepare_db):
    ts = int(prepare_db[0].timestamp_ms - (0.5 * TIMESTEP))
    response = client.get(f"?timestamp_ms={ts}&limit=2")
    assert response.status_code == 200
    all_data = response.json()
    assert len(all_data) == 2
    data = all_data

    for rep in range(0, 4):
        response = client.get(f"?timestamp_ms={data[1]['timestamp_ms']}"
                              f"&before_id={data[1]['id']}&limit=2")
        assert response.status_code == 200
        data = response.json()
        all_data.extend(data)
        if rep == 3:
            assert len(data) == 0
        else:
            assert len(data) == 2

    assert len(all_data) == 8
    assert len({x['id'] for x in all_data}) == 8


def test_duplicated_timestamp_no_id(prepare_db):
    """Messages with duplicated timestamps should all be included if no id."""
    response = client.get(f"?timestamp_ms={prepare_db[3].timestamp_ms}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 6


def test_duplicated_timestamp_with_id(prepare_db):
    """If an id is specified, can get some of the messages."""
    response = client.get(f"?timestamp_ms={prepare_db[3].timestamp_ms}"
                          f"&before_id={prepare_db[3].id}")
    assert response.status_code == 200
    data1 = response.json()
    response = client.get(f"?timestamp_ms={prepare_db[4].timestamp_ms}"
                          f"&before_id={prepare_db[4].id}")
    assert response.status_code == 200
    data2 = response.json()
    # at least one of these responses must include at least one of the
    # messages with a duplicate timestamp, but not all of them.
    assert max([len(data1), len(data2)]) > 2
    assert max([len(data1), len(data2)]) < 6


def test_delete_all():
    QTY = 40
    delete_all_loop()
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == []
    ts_ms = int(datetime.now().timestamp()*1000)
    for n in range(0, QTY):
        msg = message.StoredMessage.create(
            message.InputMessage(name=f"msg{n}", subject=f"subj{n}",
                                 text=f"Test text {n}"))
        msg.timestamp_ms = ts_ms - (TIMESTEP * n)
        msg.post()
    response = client.get(f"?limit={message.MAX_PAGE_SIZE}")
    assert response.status_code == 200
    assert len(response.json()) == min([QTY, message.MAX_PAGE_SIZE])

    response = client.delete("/")
    assert response.status_code == 204
    response = client.get(f"?limit={message.MAX_PAGE_SIZE}")
    assert response.status_code == 200
    assert len(response.json()) == 0
