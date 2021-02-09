from __future__ import annotations

import dataclasses
import enum
from typing import Optional

from . import dom, runtime
from .common import filter_unset_parameters


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


def get_event_listeners(
    objectId: runtime.RemoteObjectId,
    depth: Optional[int] = None,
    pierce: Optional[bool] = None,
):
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
    return filter_unset_parameters(
        {
            "method": "DOMDebugger.getEventListeners",
            "params": {"objectId": objectId, "depth": depth, "pierce": pierce},
        }
    )


def remove_dom_breakpoint(nodeId: dom.NodeId, type: DOMBreakpointType):
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
        "params": {"nodeId": nodeId, "type": type},
    }


def remove_event_listener_breakpoint(eventName: str, targetName: Optional[str] = None):
    """Removes breakpoint on particular DOM event.

    Parameters
    ----------
    eventName: str
            Event name.
    targetName: Optional[str]
            EventTarget interface name.
    """
    return filter_unset_parameters(
        {
            "method": "DOMDebugger.removeEventListenerBreakpoint",
            "params": {"eventName": eventName, "targetName": targetName},
        }
    )


def remove_instrumentation_breakpoint(eventName: str):
    """Removes breakpoint on particular native event.

    **Experimental**

    Parameters
    ----------
    eventName: str
            Instrumentation name to stop on.
    """
    return {
        "method": "DOMDebugger.removeInstrumentationBreakpoint",
        "params": {"eventName": eventName},
    }


def remove_xhr_breakpoint(url: str):
    """Removes breakpoint from XMLHttpRequest.

    Parameters
    ----------
    url: str
            Resource URL substring.
    """
    return {"method": "DOMDebugger.removeXHRBreakpoint", "params": {"url": url}}


def set_break_on_csp_violation(violationTypes: list[CSPViolationType]):
    """Sets breakpoint on particular CSP violations.

    **Experimental**

    Parameters
    ----------
    violationTypes: list[CSPViolationType]
            CSP Violations to stop upon.
    """
    return {
        "method": "DOMDebugger.setBreakOnCSPViolation",
        "params": {"violationTypes": violationTypes},
    }


def set_dom_breakpoint(nodeId: dom.NodeId, type: DOMBreakpointType):
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
        "params": {"nodeId": nodeId, "type": type},
    }


def set_event_listener_breakpoint(eventName: str, targetName: Optional[str] = None):
    """Sets breakpoint on particular DOM event.

    Parameters
    ----------
    eventName: str
            DOM Event name to stop on (any DOM event will do).
    targetName: Optional[str]
            EventTarget interface name to stop on. If equal to `"*"` or not provided, will stop on any
            EventTarget.
    """
    return filter_unset_parameters(
        {
            "method": "DOMDebugger.setEventListenerBreakpoint",
            "params": {"eventName": eventName, "targetName": targetName},
        }
    )


def set_instrumentation_breakpoint(eventName: str):
    """Sets breakpoint on particular native event.

    **Experimental**

    Parameters
    ----------
    eventName: str
            Instrumentation name to stop on.
    """
    return {
        "method": "DOMDebugger.setInstrumentationBreakpoint",
        "params": {"eventName": eventName},
    }


def set_xhr_breakpoint(url: str):
    """Sets breakpoint on XMLHttpRequest.

    Parameters
    ----------
    url: str
            Resource URL substring. All XHRs having this substring in the URL will get stopped upon.
    """
    return {"method": "DOMDebugger.setXHRBreakpoint", "params": {"url": url}}
