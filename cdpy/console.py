from __future__ import annotations

import dataclasses
import enum
from typing import Optional

from .common import Type, filter_unset_parameters


@dataclasses.dataclass
class ConsoleMessage(Type):
    """Console message.

    Attributes
    ----------
    source: str
            Message source.
    level: str
            Message severity.
    text: str
            Message text.
    url: Optional[str] = None
            URL of the message origin.
    line: Optional[int] = None
            Line number in the resource that generated this message (1-based).
    column: Optional[int] = None
            Column number in the resource that generated this message (1-based).
    """

    source: str
    level: str
    text: str
    url: Optional[str] = None
    line: Optional[int] = None
    column: Optional[int] = None

    @classmethod
    def from_json(cls, json: dict) -> ConsoleMessage:
        return cls(json["text"], json.get("url"), json.get("line"), json.get("column"))


def clear_messages():
    """Does nothing."""
    return {"method": "Console.clearMessages", "params": {}}


def disable():
    """Disables console domain, prevents further console messages from being reported to the client."""
    return {"method": "Console.disable", "params": {}}


def enable():
    """Enables console domain, sends the messages collected so far to the client by means of the
    `messageAdded` notification.
    """
    return {"method": "Console.enable", "params": {}}
