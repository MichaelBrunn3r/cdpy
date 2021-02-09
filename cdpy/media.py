from __future__ import annotations

import dataclasses


class PlayerId(str):
    """Players will get an ID that is unique within the agent context."""

    def __repr__(self):
        return f"PlayerId({super().__repr__()})"


class Timestamp(float):
    """"""

    def __repr__(self):
        return f"Timestamp({super().__repr__()})"


@dataclasses.dataclass
class PlayerMessage:
    """Have one type per entry in MediaLogRecord::Type
    Corresponds to kMessage

    Attributes
    ----------
    level: str
            Keep in sync with MediaLogMessageLevel
            We are currently keeping the message level 'error' separate from the
            PlayerError type because right now they represent different things,
            this one being a DVLOG(ERROR) style log message that gets printed
            based on what log level is selected in the UI, and the other is a
            representation of a media::PipelineStatus object. Soon however we're
            going to be moving away from using PipelineStatus for errors and
            introducing a new error type which should hopefully let us integrate
            the error log level into the PlayerError type.
    message: str
    """

    level: str
    message: str

    @classmethod
    def from_json(cls, json: dict) -> PlayerMessage:
        return cls(json["level"], json["message"])


@dataclasses.dataclass
class PlayerProperty:
    """Corresponds to kMediaPropertyChange

    Attributes
    ----------
    name: str
    value: str
    """

    name: str
    value: str

    @classmethod
    def from_json(cls, json: dict) -> PlayerProperty:
        return cls(json["name"], json["value"])


@dataclasses.dataclass
class PlayerEvent:
    """Corresponds to kMediaEventTriggered

    Attributes
    ----------
    timestamp: Timestamp
    value: str
    """

    timestamp: Timestamp
    value: str

    @classmethod
    def from_json(cls, json: dict) -> PlayerEvent:
        return cls(Timestamp(json["timestamp"]), json["value"])


@dataclasses.dataclass
class PlayerError:
    """Corresponds to kMediaError

    Attributes
    ----------
    type: str
    errorCode: str
            When this switches to using media::Status instead of PipelineStatus
            we can remove "errorCode" and replace it with the fields from
            a Status instance. This also seems like a duplicate of the error
            level enum - there is a todo bug to have that level removed and
            use this instead. (crbug.com/1068454)
    """

    type: str
    errorCode: str

    @classmethod
    def from_json(cls, json: dict) -> PlayerError:
        return cls(json["type"], json["errorCode"])


def enable():
    """Enables the Media domain"""
    return {"method": "Media.enable", "params": {}}


def disable():
    """Disables the Media domain."""
    return {"method": "Media.disable", "params": {}}
