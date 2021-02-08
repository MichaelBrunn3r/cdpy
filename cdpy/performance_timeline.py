from __future__ import annotations

import dataclasses
import enum
from typing import Optional

from . import dom, network, page
from .common import Type, filter_unset_parameters


@dataclasses.dataclass
class LargestContentfulPaint(Type):
    """See https://github.com/WICG/LargestContentfulPaint and largest_contentful_paint.idl

    Attributes
    ----------
    renderTime: network.TimeSinceEpoch
    loadTime: network.TimeSinceEpoch
    size: float
            The number of pixels being painted.
    elementId: Optional[str] = None
            The id attribute of the element, if available.
    url: Optional[str] = None
            The URL of the image (may be trimmed).
    nodeId: Optional[dom.BackendNodeId] = None
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


@dataclasses.dataclass
class LayoutShiftAttribution(Type):
    """
    Attributes
    ----------
    previousRect: dom.Rect
    currentRect: dom.Rect
    nodeId: Optional[dom.BackendNodeId] = None
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


@dataclasses.dataclass
class LayoutShift(Type):
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
            [LayoutShiftAttribution.from_json(x) for x in json["sources"]],
        )


@dataclasses.dataclass
class TimelineEvent(Type):
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
    duration: Optional[float] = None
            Event duration, if applicable.
    lcpDetails: Optional[LargestContentfulPaint] = None
    layoutShiftDetails: Optional[LayoutShift] = None
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


def enable(eventTypes: list[str]):
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
