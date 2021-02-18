from __future__ import annotations

import dataclasses
from typing import Optional

from ._utils import filter_none


@dataclasses.dataclass
class ConsoleMessage:
    """Console message.

    Attributes
    ----------
    source: str
            Message source.
    level: str
            Message severity.
    text: str
            Message text.
    url: Optional[str]
            URL of the message origin.
    line: Optional[int]
            Line number in the resource that generated this message (1-based).
    column: Optional[int]
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
        return cls(
            json["source"],
            json["level"],
            json["text"],
            json.get("url"),
            json.get("line"),
            json.get("column"),
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "source": self.source,
                "level": self.level,
                "text": self.text,
                "url": self.url,
                "line": self.line,
                "column": self.column,
            }
        )


def clear_messages() -> dict:
    """Does nothing."""
    return {"method": "Console.clearMessages", "params": {}}


def disable() -> dict:
    """Disables console domain, prevents further console messages from being reported to the client."""
    return {"method": "Console.disable", "params": {}}


def enable() -> dict:
    """Enables console domain, sends the messages collected so far to the client by means of the
    `messageAdded` notification.
    """
    return {"method": "Console.enable", "params": {}}


@dataclasses.dataclass
class MessageAdded:
    """Issued when new console message is added.

    Attributes
    ----------
    message: ConsoleMessage
            Console message that has been added.
    """

    message: ConsoleMessage

    @classmethod
    def from_json(cls, json: dict) -> MessageAdded:
        return cls(ConsoleMessage.from_json(json["message"]))
