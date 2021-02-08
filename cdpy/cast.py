from __future__ import annotations

import dataclasses
import enum
from typing import Optional

from .common import Type, filter_unset_parameters


@dataclasses.dataclass
class Sink(Type):
    """
    Attributes
    ----------
    name: str
    id: str
    session: Optional[str] = None
            Text describing the current session. Present only if there is an active
            session on the sink.
    """

    name: str
    id: str
    session: Optional[str] = None

    @classmethod
    def from_json(cls, json: dict) -> Sink:
        return cls(json["name"], json["id"], json.get("session"))


def enable(presentationUrl: Optional[str] = None):
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


def disable():
    """Stops observing for sinks and issues."""
    return {"method": "Cast.disable", "params": {}}


def set_sink_to_use(sinkName: str):
    """Sets a sink to be used when the web page requests the browser to choose a
    sink via Presentation API, Remote Playback API, or Cast SDK.

    Parameters
    ----------
    sinkName: str
    """
    return {"method": "Cast.setSinkToUse", "params": {"sinkName": sinkName}}


def start_tab_mirroring(sinkName: str):
    """Starts mirroring the tab to the sink.

    Parameters
    ----------
    sinkName: str
    """
    return {"method": "Cast.startTabMirroring", "params": {"sinkName": sinkName}}


def stop_casting(sinkName: str):
    """Stops the active Cast session on the sink.

    Parameters
    ----------
    sinkName: str
    """
    return {"method": "Cast.stopCasting", "params": {"sinkName": sinkName}}