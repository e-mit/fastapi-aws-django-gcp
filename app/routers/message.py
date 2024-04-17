"""Post and get text messages."""
from datetime import datetime, timezone
from typing import Annotated
from typing_extensions import Self
import uuid

from fastapi import APIRouter, status
from pydantic import BaseModel, StringConstraints


class InputMessage(BaseModel):
    name: Annotated[str, StringConstraints(max_length=20)]
    text: Annotated[str, StringConstraints(max_length=200)]


class StoredMessage(InputMessage):
    id: int
    timestamp: datetime

    @classmethod
    def create(cls, message: InputMessage) -> Self:
        msg = cls(name=message.name, text=message.text, id=uuid.uuid4().int,
                  timestamp=datetime.now(tz=timezone.utc))
        return msg


messages: list[StoredMessage] = []

router = APIRouter(tags=["Message"])


@router.get("/")
def read_messages() -> list[StoredMessage]:
    """Get message(s)."""
    return messages


@router.post("/", status_code=status.HTTP_201_CREATED)
def write_message(message: InputMessage):
    """Post a message."""
    msg = StoredMessage.create(message)
    messages.append(msg)
    return msg
