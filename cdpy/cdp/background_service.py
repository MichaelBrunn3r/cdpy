from __future__ import annotations

import dataclasses
import enum

from . import network, service_worker


class ServiceName(enum.Enum):
    """The Background Service that will be associated with the commands/events.
    Every Background Service operates independently, but they share the same
    API.
    """

    BACKGROUND_FETCH = "backgroundFetch"
    BACKGROUND_SYNC = "backgroundSync"
    PUSH_MESSAGING = "pushMessaging"
    NOTIFICATIONS = "notifications"
    PAYMENT_HANDLER = "paymentHandler"
    PERIODIC_BACKGROUND_SYNC = "periodicBackgroundSync"


@dataclasses.dataclass
class EventMetadata:
    """A key-value pair for additional event information to pass along.

    Attributes
    ----------
    key: str
    value: str
    """

    key: str
    value: str

    @classmethod
    def from_json(cls, json: dict) -> EventMetadata:
        return cls(json["key"], json["value"])

    def to_json(self):
        return {"key": self.key, "value": self.value}


@dataclasses.dataclass
class BackgroundServiceEvent:
    """
    Attributes
    ----------
    timestamp: network.TimeSinceEpoch
            Timestamp of the event (in seconds).
    origin: str
            The origin this event belongs to.
    serviceWorkerRegistrationId: service_worker.RegistrationID
            The Service Worker ID that initiated the event.
    service: ServiceName
            The Background Service this event belongs to.
    eventName: str
            A description of the event.
    instanceId: str
            An identifier that groups related events together.
    eventMetadata: list[EventMetadata]
            A list of event-specific information.
    """

    timestamp: network.TimeSinceEpoch
    origin: str
    serviceWorkerRegistrationId: service_worker.RegistrationID
    service: ServiceName
    eventName: str
    instanceId: str
    eventMetadata: list[EventMetadata]

    @classmethod
    def from_json(cls, json: dict) -> BackgroundServiceEvent:
        return cls(
            network.TimeSinceEpoch(json["timestamp"]),
            json["origin"],
            service_worker.RegistrationID(json["serviceWorkerRegistrationId"]),
            ServiceName(json["service"]),
            json["eventName"],
            json["instanceId"],
            [EventMetadata.from_json(e) for e in json["eventMetadata"]],
        )

    def to_json(self):
        return {
            "timestamp": float(self.timestamp),
            "origin": self.origin,
            "serviceWorkerRegistrationId": str(self.serviceWorkerRegistrationId),
            "service": self.service.value,
            "eventName": self.eventName,
            "instanceId": self.instanceId,
            "eventMetadata": [e.to_json() for e in self.eventMetadata],
        }


def start_observing(service: ServiceName) -> dict:
    """Enables event updates for the service.

    Parameters
    ----------
    service: ServiceName
    """
    return {
        "method": "BackgroundService.startObserving",
        "params": {"service": service.value},
    }


def stop_observing(service: ServiceName) -> dict:
    """Disables event updates for the service.

    Parameters
    ----------
    service: ServiceName
    """
    return {
        "method": "BackgroundService.stopObserving",
        "params": {"service": service.value},
    }


def set_recording(shouldRecord: bool, service: ServiceName) -> dict:
    """Set the recording state for the service.

    Parameters
    ----------
    shouldRecord: bool
    service: ServiceName
    """
    return {
        "method": "BackgroundService.setRecording",
        "params": {"shouldRecord": shouldRecord, "service": service.value},
    }


def clear_events(service: ServiceName) -> dict:
    """Clears all stored data for the service.

    Parameters
    ----------
    service: ServiceName
    """
    return {
        "method": "BackgroundService.clearEvents",
        "params": {"service": service.value},
    }


@dataclasses.dataclass
class RecordingStateChanged:
    """Called when the recording state for the service has been updated.

    Attributes
    ----------
    isRecording: bool
    service: ServiceName
    """

    isRecording: bool
    service: ServiceName

    @classmethod
    def from_json(cls, json: dict) -> RecordingStateChanged:
        return cls(json["isRecording"], ServiceName(json["service"]))


@dataclasses.dataclass
class BackgroundServiceEventReceived:
    """Called with all existing backgroundServiceEvents when enabled, and all new
    events afterwards if enabled and recording.

    Attributes
    ----------
    backgroundServiceEvent: BackgroundServiceEvent
    """

    backgroundServiceEvent: BackgroundServiceEvent

    @classmethod
    def from_json(cls, json: dict) -> BackgroundServiceEventReceived:
        return cls(BackgroundServiceEvent.from_json(json["backgroundServiceEvent"]))
