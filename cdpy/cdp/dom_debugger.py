from __future__ import annotations

import dataclasses
import enum
from typing import Generator, Optional

from . import dom, runtime
from ._utils import filter_none


class DOMBreakpointType(enum.Enum):
    """DOM breakpoint type."""

    SUBTREE_MODIFIED = "subtree-modified"
    ATTRIBUTE_MODIFIED = "attribute-modified"
    NODE_REMOVED = "node-removed"


class CSPViolationType(enum.Enum):
    """CSP Violation type."""

    TRUSTEDTYPE_SINK_VIOLATION = "trustedtype-sink-violation"
    TRUSTEDTYPE_POLICY_VIOLATION = "trustedtype-policy-violation"


@dataclasses.dataclass
class EventListener:
    """Object event listener.

    Attributes
    ----------
    type: str
            `EventListener`'s type.
    useCapture: bool
            `EventListener`'s useCapture.
    passive: bool
            `EventListener`'s passive flag.
    once: bool
            `EventListener`'s once flag.
    scriptId: runtime.ScriptId
            Script id of the handler code.
    lineNumber: int
            Line number in the script (0-based).
    columnNumber: int
            Column number in the script (0-based).
    handler: Optional[runtime.RemoteObject]
            Event handler function value.
    originalHandler: Optional[runtime.RemoteObject]
            Event original handler function value.
    backendNodeId: Optional[dom.BackendNodeId]
            Node the listener is added to (if any).
    """

    type: str
    useCapture: bool
    passive: bool
    once: bool
    scriptId: runtime.ScriptId
    lineNumber: int
    columnNumber: int
    handler: Optional[runtime.RemoteObject] = None
    originalHandler: Optional[runtime.RemoteObject] = None
    backendNodeId: Optional[dom.BackendNodeId] = None

    @classmethod
    def from_json(cls, json: dict) -> EventListener:
        return cls(
            json["type"],
            json["useCapture"],
            json["passive"],
            json["once"],
            runtime.ScriptId(json["scriptId"]),
            json["lineNumber"],
            json["columnNumber"],
            runtime.RemoteObject.from_json(json["handler"])
            if "handler" in json
            else None,
            runtime.RemoteObject.from_json(json["originalHandler"])
            if "originalHandler" in json
            else None,
            dom.BackendNodeId(json["backendNodeId"])
            if "backendNodeId" in json
            else None,
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "type": self.type,
                "useCapture": self.useCapture,
                "passive": self.passive,
                "once": self.once,
                "scriptId": str(self.scriptId),
                "lineNumber": self.lineNumber,
                "columnNumber": self.columnNumber,
                "handler": self.handler.to_json() if self.handler else None,
                "originalHandler": self.originalHandler.to_json()
                if self.originalHandler
                else None,
                "backendNodeId": int(self.backendNodeId)
                if self.backendNodeId
                else None,
            }
        )


def get_event_listeners(
    objectId: runtime.RemoteObjectId,
    depth: Optional[int] = None,
    pierce: Optional[bool] = None,
) -> Generator[dict, dict, list[EventListener]]:
    """Returns event listeners of the given object.

    Parameters
    ----------
    objectId: runtime.RemoteObjectId
            Identifier of the object to return listeners for.
    depth: Optional[int]
            The maximum depth at which Node children should be retrieved, defaults to 1. Use -1 for the
            entire subtree or provide an integer larger than 0.
    pierce: Optional[bool]
            Whether or not iframes and shadow roots should be traversed when returning the subtree
            (default is false). Reports listeners for all contexts if pierce is enabled.

    Returns
    -------
    listeners: list[EventListener]
            Array of relevant listeners.
    """
    response = yield {
        "method": "DOMDebugger.getEventListeners",
        "params": filter_none(
            {"objectId": str(objectId), "depth": depth, "pierce": pierce}
        ),
    }
    return [EventListener.from_json(l) for l in response["listeners"]]


def remove_dom_breakpoint(nodeId: dom.NodeId, type: DOMBreakpointType) -> dict:
    """Removes DOM breakpoint that was set using `setDOMBreakpoint`.

    Parameters
    ----------
    nodeId: dom.NodeId
            Identifier of the node to remove breakpoint from.
    type: DOMBreakpointType
            Type of the breakpoint to remove.
    """
    return {
        "method": "DOMDebugger.removeDOMBreakpoint",
        "params": {"nodeId": int(nodeId), "type": type.value},
    }


def remove_event_listener_breakpoint(
    eventName: str, targetName: Optional[str] = None
) -> dict:
    """Removes breakpoint on particular DOM event.

    Parameters
    ----------
    eventName: str
            Event name.
    targetName: Optional[str]
            EventTarget interface name.
    """
    return {
        "method": "DOMDebugger.removeEventListenerBreakpoint",
        "params": filter_none({"eventName": eventName, "targetName": targetName}),
    }


def remove_instrumentation_breakpoint(eventName: str) -> dict:
    """Removes breakpoint on particular native event.

    Parameters
    ----------
    eventName: str
            Instrumentation name to stop on.

    **Experimental**
    """
    return {
        "method": "DOMDebugger.removeInstrumentationBreakpoint",
        "params": {"eventName": eventName},
    }


def remove_xhr_breakpoint(url: str) -> dict:
    """Removes breakpoint from XMLHttpRequest.

    Parameters
    ----------
    url: str
            Resource URL substring.
    """
    return {"method": "DOMDebugger.removeXHRBreakpoint", "params": {"url": url}}


def set_break_on_csp_violation(violationTypes: list[CSPViolationType]) -> dict:
    """Sets breakpoint on particular CSP violations.

    Parameters
    ----------
    violationTypes: list[CSPViolationType]
            CSP Violations to stop upon.

    **Experimental**
    """
    return {
        "method": "DOMDebugger.setBreakOnCSPViolation",
        "params": {"violationTypes": [v.value for v in violationTypes]},
    }


def set_dom_breakpoint(nodeId: dom.NodeId, type: DOMBreakpointType) -> dict:
    """Sets breakpoint on particular operation with DOM.

    Parameters
    ----------
    nodeId: dom.NodeId
            Identifier of the node to set breakpoint on.
    type: DOMBreakpointType
            Type of the operation to stop upon.
    """
    return {
        "method": "DOMDebugger.setDOMBreakpoint",
        "params": {"nodeId": int(nodeId), "type": type.value},
    }


def set_event_listener_breakpoint(
    eventName: str, targetName: Optional[str] = None
) -> dict:
    """Sets breakpoint on particular DOM event.

    Parameters
    ----------
    eventName: str
            DOM Event name to stop on (any DOM event will do).
    targetName: Optional[str]
            EventTarget interface name to stop on. If equal to `"*"` or not provided, will stop on any
            EventTarget.
    """
    return {
        "method": "DOMDebugger.setEventListenerBreakpoint",
        "params": filter_none({"eventName": eventName, "targetName": targetName}),
    }


def set_instrumentation_breakpoint(eventName: str) -> dict:
    """Sets breakpoint on particular native event.

    Parameters
    ----------
    eventName: str
            Instrumentation name to stop on.

    **Experimental**
    """
    return {
        "method": "DOMDebugger.setInstrumentationBreakpoint",
        "params": {"eventName": eventName},
    }


def set_xhr_breakpoint(url: str) -> dict:
    """Sets breakpoint on XMLHttpRequest.

    Parameters
    ----------
    url: str
            Resource URL substring. All XHRs having this substring in the URL will get stopped upon.
    """
    return {"method": "DOMDebugger.setXHRBreakpoint", "params": {"url": url}}
