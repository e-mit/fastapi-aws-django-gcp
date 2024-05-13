"""Read, write and delete text messages."""

from datetime import datetime
from typing import Annotated
from typing_extensions import Self
import uuid
import logging
import os
import time

from fastapi import APIRouter, status, Query, Path
from fastapi import HTTPException, Response, Request
from pydantic import BaseModel, StringConstraints
import boto3
from boto3.dynamodb.conditions import Key

PK_VALUE = 1  # Arbitrary universal partition key value for GSI
MAX_ID_LENGTH = 39  # This is a 128-bit number
MAX_PAGE_SIZE = 30
DEFAULT_PAGE_SIZE = 10
ARBITRARY_ID = "1"
MAX_NAME_LENGTH = 20
MAX_SUBJECT_LENGTH = 40
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
    """Message as input by the client."""

    name: Annotated[str, StringConstraints(
        max_length=MAX_NAME_LENGTH, min_length=1)]
    subject: Annotated[str, StringConstraints(
        max_length=MAX_SUBJECT_LENGTH, min_length=1)]
    text: Annotated[str, StringConstraints(
        max_length=MAX_MESSAGE_LENGTH, min_length=1)]


class StoredMessage(InputMessage):
    """Message for storing in database and returning to client."""

    id: str
    timestamp_ms: int

    @classmethod
    def create(cls, message: InputMessage) -> Self:
        """Create a StoredMessage instance from an input InputMessage."""
        msg = cls(name=message.name, subject=message.subject,
                  text=message.text, id=str(uuid.uuid4().int),
                  timestamp_ms=int(datetime.now().timestamp()*1000))
        return msg

    def post(self):
        """Store the message in the database."""
        dynamo_table.put_item(
            Item={"pk": PK_VALUE, "id": self.id,
                  "timestamp_ms": self.timestamp_ms,
                  "name": self.name, "subject": self.subject,
                  "text": self.text})


@router.get("/{id}", status_code=status.HTTP_200_OK)
def read_message_by_id(
        id: Annotated[str, Path(max_length=MAX_ID_LENGTH)]
                      ) -> StoredMessage | None:
    """Get message using its id."""
    message = dynamo_table.get_item(Key={"id": id}).get("Item", None)
    if message is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Message ID not found")
    return message


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
def write_message(response: Response, request: Request,
                  message: InputMessage) -> StoredMessage:
    """Post a message."""
    msg = StoredMessage.create(message)
    msg.post()
    response.headers["Location"] = os.path.join(str(request.url), msg.id)
    return msg


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_message_by_id(id: str) -> None:
    """Delete a message using its ID."""
    dynamo_table.delete_item(Key={"id": id})


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_all() -> None:
    """Delete all messages."""
    DELETE_BATCH_LIMIT = 25
    items = dynamo_table.scan(Limit=DELETE_BATCH_LIMIT).get("Items", [])
    while len(items) > 0:
        with dynamo_table.batch_writer() as batch:
            for item in items:
                batch.delete_item(Key={'id': item['id']})
        items = dynamo_table.scan(Limit=DELETE_BATCH_LIMIT).get("Items", [])
        time.sleep(0.1)
