"""Read, write and delete text messages."""
from datetime import datetime
from typing import Annotated
from typing_extensions import Self
import uuid
import logging
import os

from fastapi import APIRouter, status, Query, Path
from pydantic import BaseModel, StringConstraints
import boto3
from boto3.dynamodb.conditions import Key

PK_VALUE = 1  # Arbitrary universal partition key value for GSI
MAX_ID_LENGTH = 39  # This is a 128-bit number
MAX_PAGE_SIZE = 30
DEFAULT_PAGE_SIZE = 10
ARBITRARY_ID = "1"
MAX_NAME_LENGTH = 20
MAX_MESSAGE_LENGTH = 200
FUTURE_SECONDS_OFFSET = 500

DB_TABLE_NAME = os.environ['DB_TABLE_NAME']
logger = logging.getLogger()
router = APIRouter(tags=["Message"])

if os.environ.get('TEST'):
    logger.info('Local test mode: using database %s', DB_TABLE_NAME)
    dynamo_table = boto3.resource('dynamodb',
                                  endpoint_url='http://localhost:8000'
                                  ).Table(DB_TABLE_NAME)
else:
    logger.info('Using database %s', DB_TABLE_NAME)
    dynamo_table = boto3.resource('dynamodb').Table(DB_TABLE_NAME)


class InputMessage(BaseModel):
    name: Annotated[str, StringConstraints(max_length=MAX_NAME_LENGTH)]
    text: Annotated[str, StringConstraints(max_length=MAX_MESSAGE_LENGTH)]


class StoredMessage(InputMessage):
    id: str
    timestamp_ms: int

    @classmethod
    def create(cls, message: InputMessage) -> Self:
        msg = cls(name=message.name, text=message.text,
                  id=str(uuid.uuid4().int),
                  timestamp_ms=int(datetime.now().timestamp()*1000))
        return msg

    def post(self):
        dynamo_table.put_item(
            Item={"pk": PK_VALUE, "id": self.id,
                  "timestamp_ms": self.timestamp_ms,
                  "name": self.name, "text": self.text})


@router.get("/{id}", status_code=status.HTTP_200_OK)
def read_message_by_id(
        id: Annotated[str, Path(max_length=MAX_ID_LENGTH)]
                      ) -> StoredMessage | None:
    """Get message using its id."""
    data = dynamo_table.get_item(Key={"id": id})
    return data.get("Item", None)


@router.get("/", status_code=status.HTTP_200_OK)
def read_messages(
        timestamp_ms: Annotated[int | None, Query(gt=0)] = None,
        before_id: Annotated[
            str | None, Query(max_length=MAX_ID_LENGTH)] = None,
        limit: Annotated[
            int, Query(gt=0, le=MAX_PAGE_SIZE)] = DEFAULT_PAGE_SIZE
        ) -> list[StoredMessage]:
    """Get paginated messages, sorted by timestamp, most recent first.

    Get all messages posted at or before the specified timestamp, or all
    messages if no timestamp is provided.
    Optionally, an ending id can also be specified (all items prior to
    this will be returned), allowing unique pagination even if
    timestamps are duplicated.
    The page size limit can also be set.
    """
    if not timestamp_ms:
        # Get a timestamp in the future
        timestamp_ms = int(
            (datetime.now().timestamp() + FUTURE_SECONDS_OFFSET)*1000)

    query_args = {
        "IndexName": "gsi",
        "ScanIndexForward": False,
        "KeyConditionExpression": (
            Key("pk").eq(PK_VALUE)
            & Key("timestamp_ms").lte(timestamp_ms)),
        "Limit": limit
    }

    if before_id:
        query_args["ExclusiveStartKey"] = {
            'id': before_id, 'pk': PK_VALUE,
            'timestamp_ms': timestamp_ms}

    return dynamo_table.query(**query_args).get("Items", [])


@router.post("/", status_code=status.HTTP_201_CREATED)
def write_message(message: InputMessage) -> StoredMessage:
    """Post a message."""
    msg = StoredMessage.create(message)
    msg.post()
    return msg


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_message(id: str) -> None:
    """Delete a message."""
    dynamo_table.delete_item(Key={"id": id})
