from __future__ import annotations

import dataclasses
from typing import Optional

from . import dom, network, page
from ._utils import filter_none


@dataclasses.dataclass
class LargestContentfulPaint:
    """See https://github.com/WICG/LargestContentfulPaint and largest_contentful_paint.idl

    Attributes
    ----------
    renderTime: network.TimeSinceEpoch
    loadTime: network.TimeSinceEpoch
    size: float
            The number of pixels being painted.
    elementId: Optional[str]
            The id attribute of the element, if available.
    url: Optional[str]
            The URL of the image (may be trimmed).
    nodeId: Optional[dom.BackendNodeId]
    """

    renderTime: network.TimeSinceEpoch
    loadTime: network.TimeSinceEpoch
    size: float
    elementId: Optional[str] = None
    url: Optional[str] = None
    nodeId: Optional[dom.BackendNodeId] = None

    @classmethod
    def from_json(cls, json: dict) -> LargestContentfulPaint:
        return cls(
            network.TimeSinceEpoch(json["renderTime"]),
            network.TimeSinceEpoch(json["loadTime"]),
            json["size"],
            json.get("elementId"),
            json.get("url"),
            dom.BackendNodeId(json["nodeId"]) if "nodeId" in json else None,
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "renderTime": float(self.renderTime),
                "loadTime": float(self.loadTime),
                "size": self.size,
                "elementId": self.elementId,
                "url": self.url,
                "nodeId": int(self.nodeId) if self.nodeId else None,
            }
        )


@dataclasses.dataclass
class LayoutShiftAttribution:
    """
    Attributes
    ----------
    previousRect: dom.Rect
    currentRect: dom.Rect
    nodeId: Optional[dom.BackendNodeId]
    """

    previousRect: dom.Rect
    currentRect: dom.Rect
    nodeId: Optional[dom.BackendNodeId] = None

    @classmethod
    def from_json(cls, json: dict) -> LayoutShiftAttribution:
        return cls(
            dom.Rect.from_json(json["previousRect"]),
            dom.Rect.from_json(json["currentRect"]),
            dom.BackendNodeId(json["nodeId"]) if "nodeId" in json else None,
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "previousRect": self.previousRect.to_json(),
                "currentRect": self.currentRect.to_json(),
                "nodeId": int(self.nodeId) if self.nodeId else None,
            }
        )


@dataclasses.dataclass
class LayoutShift:
    """See https://wicg.github.io/layout-instability/#sec-layout-shift and layout_shift.idl

    Attributes
    ----------
    value: float
            Score increment produced by this event.
    hadRecentInput: bool
    lastInputTime: network.TimeSinceEpoch
    sources: list[LayoutShiftAttribution]
    """

    value: float
    hadRecentInput: bool
    lastInputTime: network.TimeSinceEpoch
    sources: list[LayoutShiftAttribution]

    @classmethod
    def from_json(cls, json: dict) -> LayoutShift:
        return cls(
            json["value"],
            json["hadRecentInput"],
            network.TimeSinceEpoch(json["lastInputTime"]),
            [LayoutShiftAttribution.from_json(s) for s in json["sources"]],
        )

    def to_json(self) -> dict:
        return {
            "value": self.value,
            "hadRecentInput": self.hadRecentInput,
            "lastInputTime": float(self.lastInputTime),
            "sources": [s.to_json() for s in self.sources],
        }


@dataclasses.dataclass
class TimelineEvent:
    """
    Attributes
    ----------
    frameId: page.FrameId
            Identifies the frame that this event is related to. Empty for non-frame targets.
    type: str
            The event type, as specified in https://w3c.github.io/performance-timeline/#dom-performanceentry-entrytype
            This determines which of the optional "details" fiedls is present.
    name: str
            Name may be empty depending on the type.
    time: network.TimeSinceEpoch
            Time in seconds since Epoch, monotonically increasing within document lifetime.
    duration: Optional[float]
            Event duration, if applicable.
    lcpDetails: Optional[LargestContentfulPaint]
    layoutShiftDetails: Optional[LayoutShift]
    """

    frameId: page.FrameId
    type: str
    name: str
    time: network.TimeSinceEpoch
    duration: Optional[float] = None
    lcpDetails: Optional[LargestContentfulPaint] = None
    layoutShiftDetails: Optional[LayoutShift] = None

    @classmethod
    def from_json(cls, json: dict) -> TimelineEvent:
        return cls(
            page.FrameId(json["frameId"]),
            json["type"],
            json["name"],
            network.TimeSinceEpoch(json["time"]),
            json.get("duration"),
            LargestContentfulPaint.from_json(json["lcpDetails"])
            if "lcpDetails" in json
            else None,
            LayoutShift.from_json(json["layoutShiftDetails"])
            if "layoutShiftDetails" in json
            else None,
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "frameId": str(self.frameId),
                "type": self.type,
                "name": self.name,
                "time": float(self.time),
                "duration": self.duration,
                "lcpDetails": self.lcpDetails.to_json() if self.lcpDetails else None,
                "layoutShiftDetails": self.layoutShiftDetails.to_json()
                if self.layoutShiftDetails
                else None,
            }
        )


def enable(eventTypes: list[str]) -> dict:
    """Previously buffered events would be reported before method returns.
    See also: timelineEventAdded

    Parameters
    ----------
    eventTypes: list[str]
            The types of event to report, as specified in
            https://w3c.github.io/performance-timeline/#dom-performanceentry-entrytype
            The specified filter overrides any previous filters, passing empty
            filter disables recording.
            Note that not all types exposed to the web platform are currently supported.
    """
    return {
        "method": "PerformanceTimeline.enable",
        "params": {"eventTypes": eventTypes},
    }


@dataclasses.dataclass
class TimelineEventAdded:
    """Sent when a performance timeline event is added. See reportPerformanceTimeline method.

    Attributes
    ----------
    event: TimelineEvent
    """

    event: TimelineEvent

    @classmethod
    def from_json(cls, json: dict) -> TimelineEventAdded:
        return cls(TimelineEvent.from_json(json["event"]))
