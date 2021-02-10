from __future__ import annotations

import dataclasses
from typing import Optional

from . import network, runtime
from .common import filter_none


@dataclasses.dataclass
class LogEntry:
    """Log entry.

    Attributes
    ----------
    source: str
            Log entry source.
    level: str
            Log entry severity.
    text: str
            Logged text.
    timestamp: runtime.Timestamp
            Timestamp when this entry was added.
    url: Optional[str]
            URL of the resource if known.
    lineNumber: Optional[int]
            Line number in the resource.
    stackTrace: Optional[runtime.StackTrace]
            JavaScript stack trace.
    networkRequestId: Optional[network.RequestId]
            Identifier of the network request associated with this entry.
    workerId: Optional[str]
            Identifier of the worker associated with this entry.
    args: Optional[list[runtime.RemoteObject]]
            Call arguments.
    """

    source: str
    level: str
    text: str
    timestamp: runtime.Timestamp
    url: Optional[str] = None
    lineNumber: Optional[int] = None
    stackTrace: Optional[runtime.StackTrace] = None
    networkRequestId: Optional[network.RequestId] = None
    workerId: Optional[str] = None
    args: Optional[list[runtime.RemoteObject]] = None

    @classmethod
    def from_json(cls, json: dict) -> LogEntry:
        return cls(
            json["source"],
            json["level"],
            json["text"],
            runtime.Timestamp(json["timestamp"]),
            json.get("url"),
            json.get("lineNumber"),
            runtime.StackTrace.from_json(json["stackTrace"])
            if "stackTrace" in json
            else None,
            network.RequestId(json["networkRequestId"])
            if "networkRequestId" in json
            else None,
            json.get("workerId"),
            [runtime.RemoteObject.from_json(a) for a in json["args"]]
            if "args" in json
            else None,
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "source": self.source,
                "level": self.level,
                "text": self.text,
                "timestamp": float(self.timestamp),
                "url": self.url,
                "lineNumber": self.lineNumber,
                "stackTrace": self.stackTrace.to_json() if self.stackTrace else None,
                "networkRequestId": str(self.networkRequestId)
                if self.networkRequestId
                else None,
                "workerId": self.workerId,
                "args": [a.to_json() for a in self.args] if self.args else None,
            }
        )


@dataclasses.dataclass
class ViolationSetting:
    """Violation configuration setting.

    Attributes
    ----------
    name: str
            Violation type.
    threshold: float
            Time threshold to trigger upon.
    """

    name: str
    threshold: float

    @classmethod
    def from_json(cls, json: dict) -> ViolationSetting:
        return cls(json["name"], json["threshold"])

    def to_json(self) -> dict:
        return {"name": self.name, "threshold": self.threshold}


def clear() -> dict:
    """Clears the log."""
    return {"method": "Log.clear", "params": {}}


def disable() -> dict:
    """Disables log domain, prevents further log entries from being reported to the client."""
    return {"method": "Log.disable", "params": {}}


def enable() -> dict:
    """Enables log domain, sends the entries collected so far to the client by means of the
    `entryAdded` notification.
    """
    return {"method": "Log.enable", "params": {}}


def start_violations_report(config: list[ViolationSetting]) -> dict:
    """start violation reporting.

    Parameters
    ----------
    config: list[ViolationSetting]
            Configuration for violations.
    """
    return {"method": "Log.startViolationsReport", "params": {"config": config}}


def stop_violations_report() -> dict:
    """Stop violation reporting."""
    return {"method": "Log.stopViolationsReport", "params": {}}


@dataclasses.dataclass
class EntryAdded:
    """Issued when new message was logged.

    Attributes
    ----------
    entry: LogEntry
            The entry.
    """

    entry: LogEntry

    @classmethod
    def from_json(cls, json: dict) -> EntryAdded:
        return cls(LogEntry.from_json(json["entry"]))
