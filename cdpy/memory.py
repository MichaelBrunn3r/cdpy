from __future__ import annotations

import dataclasses
import enum
from typing import Generator, Optional

from .common import filter_unset_parameters


class PressureLevel(enum.Enum):
    """Memory pressure level."""

    MODERATE = "moderate"
    CRITICAL = "critical"


@dataclasses.dataclass
class SamplingProfileNode:
    """Heap profile sample.

    Attributes
    ----------
    size: float
            Size of the sampled allocation.
    total: float
            Total bytes attributed to this sample.
    stack: list[str]
            Execution stack at the point of allocation.
    """

    size: float
    total: float
    stack: list[str]

    @classmethod
    def from_json(cls, json: dict) -> SamplingProfileNode:
        return cls(json["size"], json["total"], json["stack"])

    def to_json(self) -> dict:
        return {"size": self.size, "total": self.total, "stack": self.stack}


@dataclasses.dataclass
class SamplingProfile:
    """Array of heap profile samples.

    Attributes
    ----------
    samples: list[SamplingProfileNode]
    modules: list[Module]
    """

    samples: list[SamplingProfileNode]
    modules: list[Module]

    @classmethod
    def from_json(cls, json: dict) -> SamplingProfile:
        return cls(
            [SamplingProfileNode.from_json(s) for s in json["samples"]],
            [Module.from_json(m) for m in json["modules"]],
        )

    def to_json(self) -> dict:
        return {
            "samples": [s.to_json() for s in self.samples],
            "modules": [m.to_json() for m in self.modules],
        }


@dataclasses.dataclass
class Module:
    """Executable module information

    Attributes
    ----------
    name: str
            Name of the module.
    uuid: str
            UUID of the module.
    baseAddress: str
            Base address where the module is loaded into memory. Encoded as a decimal
            or hexadecimal (0x prefixed) string.
    size: float
            Size of the module in bytes.
    """

    name: str
    uuid: str
    baseAddress: str
    size: float

    @classmethod
    def from_json(cls, json: dict) -> Module:
        return cls(json["name"], json["uuid"], json["baseAddress"], json["size"])

    def to_json(self) -> dict:
        return {
            "name": self.name,
            "uuid": self.uuid,
            "baseAddress": self.baseAddress,
            "size": self.size,
        }


def get_dom_counters() -> Generator[dict, dict, dict]:
    """
    Returns
    -------
    documents: int
    nodes: int
    jsEventListeners: int
    """
    response = yield {"method": "Memory.getDOMCounters", "params": {}}
    return {
        "documents": response["documents"],
        "nodes": response["nodes"],
        "jsEventListeners": response["jsEventListeners"],
    }


def prepare_for_leak_detection() -> dict:
    """"""
    return {"method": "Memory.prepareForLeakDetection", "params": {}}


def forcibly_purge_java_script_memory() -> dict:
    """Simulate OomIntervention by purging V8 memory."""
    return {"method": "Memory.forciblyPurgeJavaScriptMemory", "params": {}}


def set_pressure_notifications_suppressed(suppressed: bool) -> dict:
    """Enable/disable suppressing memory pressure notifications in all processes.

    Parameters
    ----------
    suppressed: bool
            If true, memory pressure notifications will be suppressed.
    """
    return {
        "method": "Memory.setPressureNotificationsSuppressed",
        "params": {"suppressed": suppressed},
    }


def simulate_pressure_notification(level: PressureLevel) -> dict:
    """Simulate a memory pressure notification in all processes.

    Parameters
    ----------
    level: PressureLevel
            Memory pressure level of the notification.
    """
    return {
        "method": "Memory.simulatePressureNotification",
        "params": {"level": level.value},
    }


def start_sampling(
    samplingInterval: Optional[int] = None, suppressRandomness: Optional[bool] = None
) -> dict:
    """Start collecting native memory profile.

    Parameters
    ----------
    samplingInterval: Optional[int]
            Average number of bytes between samples.
    suppressRandomness: Optional[bool]
            Do not randomize intervals between samples.
    """
    return filter_unset_parameters(
        {
            "method": "Memory.startSampling",
            "params": {
                "samplingInterval": samplingInterval,
                "suppressRandomness": suppressRandomness,
            },
        }
    )


def stop_sampling() -> dict:
    """Stop collecting native memory profile."""
    return {"method": "Memory.stopSampling", "params": {}}


def get_all_time_sampling_profile() -> Generator[dict, dict, SamplingProfile]:
    """Retrieve native memory allocations profile
    collected since renderer process startup.

    Returns
    -------
    profile: SamplingProfile
    """
    response = yield {"method": "Memory.getAllTimeSamplingProfile", "params": {}}
    return SamplingProfile.from_json(response)


def get_browser_sampling_profile() -> Generator[dict, dict, SamplingProfile]:
    """Retrieve native memory allocations profile
    collected since browser process startup.

    Returns
    -------
    profile: SamplingProfile
    """
    response = yield {"method": "Memory.getBrowserSamplingProfile", "params": {}}
    return SamplingProfile.from_json(response)


def get_sampling_profile() -> Generator[dict, dict, SamplingProfile]:
    """Retrieve native memory allocations profile collected since last
    `startSampling` call.

    Returns
    -------
    profile: SamplingProfile
    """
    response = yield {"method": "Memory.getSamplingProfile", "params": {}}
    return SamplingProfile.from_json(response)
