from __future__ import annotations

import dataclasses


def disable() -> dict:
    """Disables inspector domain notifications."""
    return {"method": "Inspector.disable", "params": {}}


def enable() -> dict:
    """Enables inspector domain notifications."""
    return {"method": "Inspector.enable", "params": {}}


@dataclasses.dataclass
class Detached:
    """Fired when remote debugging connection is about to be terminated. Contains detach reason.

    Attributes
    ----------
    reason: str
            The reason why connection has been terminated.
    """

    reason: str

    @classmethod
    def from_json(cls, json: dict) -> Detached:
        return cls(json["reason"])


@dataclasses.dataclass
class TargetCrashed:
    """Fired when debugging target has crashed"""

    @classmethod
    def from_json(cls, json: dict) -> TargetCrashed:
        return cls()


@dataclasses.dataclass
class TargetReloadedAfterCrash:
    """Fired when debugging target has reloaded after crash"""

    @classmethod
    def from_json(cls, json: dict) -> TargetReloadedAfterCrash:
        return cls()
