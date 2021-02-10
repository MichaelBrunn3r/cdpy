from __future__ import annotations

import dataclasses
from typing import Optional

from .common import filter_none, filter_unset_parameters


@dataclasses.dataclass
class Sink:
    """
    Attributes
    ----------
    name: str
    id: str
    session: Optional[str]
            Text describing the current session. Present only if there is an active
            session on the sink.
    """

    name: str
    id: str
    session: Optional[str] = None

    @classmethod
    def from_json(cls, json: dict) -> Sink:
        return cls(json["name"], json["id"], json.get("session"))

    def to_json(self) -> dict:
        return filter_none({"name": self.name, "id": self.id, "session": self.session})


def enable(presentationUrl: Optional[str] = None) -> dict:
    """Starts observing for sinks that can be used for tab mirroring, and if set,
    sinks compatible with |presentationUrl| as well. When sinks are found, a
    |sinksUpdated| event is fired.
    Also starts observing for issue messages. When an issue is added or removed,
    an |issueUpdated| event is fired.

    Parameters
    ----------
    presentationUrl: Optional[str]
    """
    return filter_unset_parameters(
        {"method": "Cast.enable", "params": {"presentationUrl": presentationUrl}}
    )


def disable() -> dict:
    """Stops observing for sinks and issues."""
    return {"method": "Cast.disable", "params": {}}


def set_sink_to_use(sinkName: str) -> dict:
    """Sets a sink to be used when the web page requests the browser to choose a
    sink via Presentation API, Remote Playback API, or Cast SDK.

    Parameters
    ----------
    sinkName: str
    """
    return {"method": "Cast.setSinkToUse", "params": {"sinkName": sinkName}}


def start_tab_mirroring(sinkName: str) -> dict:
    """Starts mirroring the tab to the sink.

    Parameters
    ----------
    sinkName: str
    """
    return {"method": "Cast.startTabMirroring", "params": {"sinkName": sinkName}}


def stop_casting(sinkName: str) -> dict:
    """Stops the active Cast session on the sink.

    Parameters
    ----------
    sinkName: str
    """
    return {"method": "Cast.stopCasting", "params": {"sinkName": sinkName}}


@dataclasses.dataclass
class SinksUpdated:
    """This is fired whenever the list of available sinks changes. A sink is a
    device or a software surface that you can cast to.

    Attributes
    ----------
    sinks: list[Sink]
    """

    sinks: list[Sink]

    @classmethod
    def from_json(cls, json: dict) -> SinksUpdated:
        return cls([Sink.from_json(s) for s in json["sinks"]])


@dataclasses.dataclass
class IssueUpdated:
    """This is fired whenever the outstanding issue/error message changes.
    |issueMessage| is empty if there is no issue.

    Attributes
    ----------
    issueMessage: str
    """

    issueMessage: str

    @classmethod
    def from_json(cls, json: dict) -> IssueUpdated:
        return cls(json["issueMessage"])
