from __future__ import annotations

import dataclasses
import enum
from typing import Optional

from . import target
from .common import filter_none


class RegistrationID(str):
    """"""

    def __repr__(self):
        return f"RegistrationID({super().__repr__()})"


@dataclasses.dataclass
class ServiceWorkerRegistration:
    """ServiceWorker registration.

    Attributes
    ----------
    registrationId: RegistrationID
    scopeURL: str
    isDeleted: bool
    """

    registrationId: RegistrationID
    scopeURL: str
    isDeleted: bool

    @classmethod
    def from_json(cls, json: dict) -> ServiceWorkerRegistration:
        return cls(
            RegistrationID(json["registrationId"]), json["scopeURL"], json["isDeleted"]
        )

    def to_json(self) -> dict:
        return {
            "registrationId": str(self.registrationId),
            "scopeURL": self.scopeURL,
            "isDeleted": self.isDeleted,
        }


class ServiceWorkerVersionRunningStatus(enum.Enum):
    """"""

    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"


class ServiceWorkerVersionStatus(enum.Enum):
    """"""

    NEW = "new"
    INSTALLING = "installing"
    INSTALLED = "installed"
    ACTIVATING = "activating"
    ACTIVATED = "activated"
    REDUNDANT = "redundant"


@dataclasses.dataclass
class ServiceWorkerVersion:
    """ServiceWorker version.

    Attributes
    ----------
    versionId: str
    registrationId: RegistrationID
    scriptURL: str
    runningStatus: ServiceWorkerVersionRunningStatus
    status: ServiceWorkerVersionStatus
    scriptLastModified: Optional[float]
            The Last-Modified header value of the main script.
    scriptResponseTime: Optional[float]
            The time at which the response headers of the main script were received from the server.
            For cached script it is the last time the cache entry was validated.
    controlledClients: Optional[list[target.TargetID]]
    targetId: Optional[target.TargetID]
    """

    versionId: str
    registrationId: RegistrationID
    scriptURL: str
    runningStatus: ServiceWorkerVersionRunningStatus
    status: ServiceWorkerVersionStatus
    scriptLastModified: Optional[float] = None
    scriptResponseTime: Optional[float] = None
    controlledClients: Optional[list[target.TargetID]] = None
    targetId: Optional[target.TargetID] = None

    @classmethod
    def from_json(cls, json: dict) -> ServiceWorkerVersion:
        return cls(
            json["versionId"],
            RegistrationID(json["registrationId"]),
            json["scriptURL"],
            ServiceWorkerVersionRunningStatus(json["runningStatus"]),
            ServiceWorkerVersionStatus(json["status"]),
            json.get("scriptLastModified"),
            json.get("scriptResponseTime"),
            [target.TargetID(x) for x in json["controlledClients"]]
            if "controlledClients" in json
            else None,
            target.TargetID(json["targetId"]) if "targetId" in json else None,
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "versionId": self.versionId,
                "registrationId": str(self.registrationId),
                "scriptURL": self.scriptURL,
                "runningStatus": str(self.runningStatus),
                "status": str(self.status),
                "scriptLastModified": self.scriptLastModified,
                "scriptResponseTime": self.scriptResponseTime,
                "controlledClients": [str(c) for c in self.controlledClients]
                if self.controlledClients
                else None,
                "targetId": str(self.targetId) if self.targetId else None,
            }
        )


@dataclasses.dataclass
class ServiceWorkerErrorMessage:
    """ServiceWorker error message.

    Attributes
    ----------
    errorMessage: str
    registrationId: RegistrationID
    versionId: str
    sourceURL: str
    lineNumber: int
    columnNumber: int
    """

    errorMessage: str
    registrationId: RegistrationID
    versionId: str
    sourceURL: str
    lineNumber: int
    columnNumber: int

    @classmethod
    def from_json(cls, json: dict) -> ServiceWorkerErrorMessage:
        return cls(
            json["errorMessage"],
            RegistrationID(json["registrationId"]),
            json["versionId"],
            json["sourceURL"],
            json["lineNumber"],
            json["columnNumber"],
        )

    def to_json(self) -> dict:
        return {
            "errorMessage": self.errorMessage,
            "registrationId": str(self.registrationId),
            "versionId": self.versionId,
            "sourceURL": self.sourceURL,
            "lineNumber": self.lineNumber,
            "columnNumber": self.columnNumber,
        }


def deliver_push_message(origin: str, registrationId: RegistrationID, data: str):
    """
    Parameters
    ----------
    origin: str
    registrationId: RegistrationID
    data: str
    """
    return {
        "method": "ServiceWorker.deliverPushMessage",
        "params": {"origin": origin, "registrationId": registrationId, "data": data},
    }


def disable():
    """"""
    return {"method": "ServiceWorker.disable", "params": {}}


def dispatch_sync_event(
    origin: str, registrationId: RegistrationID, tag: str, lastChance: bool
):
    """
    Parameters
    ----------
    origin: str
    registrationId: RegistrationID
    tag: str
    lastChance: bool
    """
    return {
        "method": "ServiceWorker.dispatchSyncEvent",
        "params": {
            "origin": origin,
            "registrationId": registrationId,
            "tag": tag,
            "lastChance": lastChance,
        },
    }


def dispatch_periodic_sync_event(origin: str, registrationId: RegistrationID, tag: str):
    """
    Parameters
    ----------
    origin: str
    registrationId: RegistrationID
    tag: str
    """
    return {
        "method": "ServiceWorker.dispatchPeriodicSyncEvent",
        "params": {"origin": origin, "registrationId": registrationId, "tag": tag},
    }


def enable():
    """"""
    return {"method": "ServiceWorker.enable", "params": {}}


def inspect_worker(versionId: str):
    """
    Parameters
    ----------
    versionId: str
    """
    return {"method": "ServiceWorker.inspectWorker", "params": {"versionId": versionId}}


def set_force_update_on_page_load(forceUpdateOnPageLoad: bool):
    """
    Parameters
    ----------
    forceUpdateOnPageLoad: bool
    """
    return {
        "method": "ServiceWorker.setForceUpdateOnPageLoad",
        "params": {"forceUpdateOnPageLoad": forceUpdateOnPageLoad},
    }


def skip_waiting(scopeURL: str):
    """
    Parameters
    ----------
    scopeURL: str
    """
    return {"method": "ServiceWorker.skipWaiting", "params": {"scopeURL": scopeURL}}


def start_worker(scopeURL: str):
    """
    Parameters
    ----------
    scopeURL: str
    """
    return {"method": "ServiceWorker.startWorker", "params": {"scopeURL": scopeURL}}


def stop_all_workers():
    """"""
    return {"method": "ServiceWorker.stopAllWorkers", "params": {}}


def stop_worker(versionId: str):
    """
    Parameters
    ----------
    versionId: str
    """
    return {"method": "ServiceWorker.stopWorker", "params": {"versionId": versionId}}


def unregister(scopeURL: str):
    """
    Parameters
    ----------
    scopeURL: str
    """
    return {"method": "ServiceWorker.unregister", "params": {"scopeURL": scopeURL}}


def update_registration(scopeURL: str):
    """
    Parameters
    ----------
    scopeURL: str
    """
    return {
        "method": "ServiceWorker.updateRegistration",
        "params": {"scopeURL": scopeURL},
    }
