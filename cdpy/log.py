from __future__ import annotations

import dataclasses
import enum
from typing import Optional

from . import network, runtime
from .common import Type, filter_unset_parameters


@dataclasses.dataclass
class LogEntry(Type):
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
    url: Optional[str] = None
            URL of the resource if known.
    lineNumber: Optional[int] = None
            Line number in the resource.
    stackTrace: Optional[runtime.StackTrace] = None
            JavaScript stack trace.
    networkRequestId: Optional[network.RequestId] = None
            Identifier of the network request associated with this entry.
    workerId: Optional[str] = None
            Identifier of the worker associated with this entry.
    args: Optional[list[runtime.RemoteObject]] = None
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
            [runtime.RemoteObject.from_json(x) for x in json["args"]]
            if "args" in json
            else None,
        )


@dataclasses.dataclass
class ViolationSetting(Type):
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
        return cls(json["threshold"])


def clear():
    """Clears the log."""
    return {"method": "Log.clear", "params": {}}


def disable():
    """Disables log domain, prevents further log entries from being reported to the client."""
    return {"method": "Log.disable", "params": {}}


def enable():
    """Enables log domain, sends the entries collected so far to the client by means of the
    `entryAdded` notification.
    """
    return {"method": "Log.enable", "params": {}}


def start_violations_report(config: list[ViolationSetting]):
    """start violation reporting.

    Parameters
    ----------
    config: list[ViolationSetting]
            Configuration for violations.
    """
    return {"method": "Log.startViolationsReport", "params": {"config": config}}


def stop_violations_report():
    """Stop violation reporting."""
    return {"method": "Log.stopViolationsReport", "params": {}}
