from __future__ import annotations

import dataclasses
import enum
from typing import Optional

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
            [SamplingProfileNode.from_json(x) for x in json["samples"]],
            [Module.from_json(x) for x in json["modules"]],
        )


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


def get_dom_counters():
    """
    Returns
    -------
    documents: int
    nodes: int
    jsEventListeners: int
    """
    return {"method": "Memory.getDOMCounters", "params": {}}


def prepare_for_leak_detection():
    """"""
    return {"method": "Memory.prepareForLeakDetection", "params": {}}


def forcibly_purge_java_script_memory():
    """Simulate OomIntervention by purging V8 memory."""
    return {"method": "Memory.forciblyPurgeJavaScriptMemory", "params": {}}


def set_pressure_notifications_suppressed(suppressed: bool):
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


def simulate_pressure_notification(level: PressureLevel):
    """Simulate a memory pressure notification in all processes.

    Parameters
    ----------
    level: PressureLevel
            Memory pressure level of the notification.
    """
    return {"method": "Memory.simulatePressureNotification", "params": {"level": level}}


def start_sampling(
    samplingInterval: Optional[int] = None, suppressRandomness: Optional[bool] = None
):
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


def stop_sampling():
    """Stop collecting native memory profile."""
    return {"method": "Memory.stopSampling", "params": {}}


def get_all_time_sampling_profile():
    """Retrieve native memory allocations profile
    collected since renderer process startup.

    Returns
    -------
    profile: SamplingProfile
    """
    return {"method": "Memory.getAllTimeSamplingProfile", "params": {}}


def get_browser_sampling_profile():
    """Retrieve native memory allocations profile
    collected since browser process startup.

    Returns
    -------
    profile: SamplingProfile
    """
    return {"method": "Memory.getBrowserSamplingProfile", "params": {}}


def get_sampling_profile():
    """Retrieve native memory allocations profile collected since last
    `startSampling` call.

    Returns
    -------
    profile: SamplingProfile
    """
    return {"method": "Memory.getSamplingProfile", "params": {}}
