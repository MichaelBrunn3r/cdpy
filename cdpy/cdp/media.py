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

    def to_json(self):
        return {"level": self.level, "message": self.message}


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

    def to_json(self):
        return {"name": self.name, "value": self.value}


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

    def to_json(self):
        return {"timestamp": float(self.timestamp), "value": self.value}


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

    def to_json(self):
        return {"type": self.type, "errorCode": self.errorCode}


def enable() -> dict:
    """Enables the Media domain"""
    return {"method": "Media.enable", "params": {}}


def disable() -> dict:
    """Disables the Media domain."""
    return {"method": "Media.disable", "params": {}}


@dataclasses.dataclass
class PlayerPropertiesChanged:
    """This can be called multiple times, and can be used to set / override /
    remove player properties. A null propValue indicates removal.

    Attributes
    ----------
    playerId: PlayerId
    properties: list[PlayerProperty]
    """

    playerId: PlayerId
    properties: list[PlayerProperty]

    @classmethod
    def from_json(cls, json: dict) -> PlayerPropertiesChanged:
        return cls(
            PlayerId(json["playerId"]),
            [PlayerProperty.from_json(p) for p in json["properties"]],
        )


@dataclasses.dataclass
class PlayerEventsAdded:
    """Send events as a list, allowing them to be batched on the browser for less
    congestion. If batched, events must ALWAYS be in chronological order.

    Attributes
    ----------
    playerId: PlayerId
    events: list[PlayerEvent]
    """

    playerId: PlayerId
    events: list[PlayerEvent]

    @classmethod
    def from_json(cls, json: dict) -> PlayerEventsAdded:
        return cls(
            PlayerId(json["playerId"]),
            [PlayerEvent.from_json(e) for e in json["events"]],
        )


@dataclasses.dataclass
class PlayerMessagesLogged:
    """Send a list of any messages that need to be delivered.

    Attributes
    ----------
    playerId: PlayerId
    messages: list[PlayerMessage]
    """

    playerId: PlayerId
    messages: list[PlayerMessage]

    @classmethod
    def from_json(cls, json: dict) -> PlayerMessagesLogged:
        return cls(
            PlayerId(json["playerId"]),
            [PlayerMessage.from_json(m) for m in json["messages"]],
        )


@dataclasses.dataclass
class PlayerErrorsRaised:
    """Send a list of any errors that need to be delivered.

    Attributes
    ----------
    playerId: PlayerId
    errors: list[PlayerError]
    """

    playerId: PlayerId
    errors: list[PlayerError]

    @classmethod
    def from_json(cls, json: dict) -> PlayerErrorsRaised:
        return cls(
            PlayerId(json["playerId"]),
            [PlayerError.from_json(e) for e in json["errors"]],
        )


@dataclasses.dataclass
class PlayersCreated:
    """Called whenever a player is created, or when a new agent joins and recieves
    a list of active players. If an agent is restored, it will recieve the full
    list of player ids and all events again.

    Attributes
    ----------
    players: list[PlayerId]
    """

    players: list[PlayerId]

    @classmethod
    def from_json(cls, json: dict) -> PlayersCreated:
        return cls([PlayerId(p) for p in json["players"]])
