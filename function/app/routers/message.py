"""Post and get text messages."""
from datetime import datetime, timezone
from typing import Annotated
from typing_extensions import Self
import uuid
import logging
import os

from fastapi import APIRouter, status
from pydantic import BaseModel, StringConstraints
import boto3
from boto3.dynamodb.conditions import Key

DB_TABLE_NAME = os.environ['DB_TABLE_NAME']
PK_VALUE = 1
logger = logging.getLogger()

if os.environ.get('TEST'):
    logger.info('Local test mode: using database %s', DB_TABLE_NAME)
    dynamo_table = boto3.resource('dynamodb',
                                  endpoint_url='http://localhost:8000'
                                  ).Table(DB_TABLE_NAME)
else:
    logger.info('Using database %s', DB_TABLE_NAME)
    dynamo_table = boto3.resource('dynamodb').Table(DB_TABLE_NAME)


class InputMessage(BaseModel):
    name: Annotated[str, StringConstraints(max_length=20)]
    text: Annotated[str, StringConstraints(max_length=200)]


class StoredMessage(InputMessage):
    id: str
    timestamp: datetime

    @classmethod
    def create(cls, message: InputMessage) -> Self:
        msg = cls(name=message.name, text=message.text,
                  id=str(uuid.uuid4().int),
                  timestamp=datetime.now(tz=timezone.utc))
        return msg

    def post(self):
        dynamo_table.put_item(
            Item={"pk": PK_VALUE, "id": self.id,
                  "timestamp": int(self.timestamp.timestamp()),
                  "name": self.name, "text": self.text})


router = APIRouter(tags=["Message"])


@router.get("/")
def read_messages() -> list[StoredMessage]:
    """Get message(s), sorted by timestamp, most recent first."""
    response = dynamo_table.query(
        IndexName="gsi",
        ScanIndexForward=False,
        KeyConditionExpression=(
            Key("pk").eq(PK_VALUE) & Key("timestamp").gt(0)))
    return response['Items']


@router.post("/", status_code=status.HTTP_201_CREATED)
def write_message(message: InputMessage):
    """Post a message."""
    msg = StoredMessage.create(message)
    msg.post()
    return msg


@router.delete("/{id}")
def delete_message(id: str):
    """Delete a message."""
    dynamo_table.delete_item(Key={"id": id})


# As above but with pagination in groups of 2, and change query criteria
# print()
# results = []
# scan_kwargs = {
#     "IndexName": "gsi",
#     "ScanIndexForward": False,
#     "KeyConditionExpression": (
#         Key("pk").eq(1) & Key("timestamp").lt(int(ts - 1))),
#     "Limit": 2
# }
# done = False
# start_key = None
# while not done:
#     if start_key:
#         scan_kwargs["ExclusiveStartKey"] = start_key
#     response = dynamo_table.query(**scan_kwargs)
#     new_results = response.get("Items", [])
#     print(new_results)
#     results.extend(new_results)
#     start_key = response.get("LastEvaluatedKey", None)
#     done = start_key is None