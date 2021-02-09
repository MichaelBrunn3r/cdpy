from __future__ import annotations

import dataclasses
from typing import Optional

from . import browser, page
from .common import filter_unset_parameters


class TargetID(str):
    """"""

    def __repr__(self):
        return f"TargetID({super().__repr__()})"


class SessionID(str):
    """Unique identifier of attached debugging session."""

    def __repr__(self):
        return f"SessionID({super().__repr__()})"


@dataclasses.dataclass
class TargetInfo:
    """
    Attributes
    ----------
    targetId: TargetID
    type: str
    title: str
    url: str
    attached: bool
            Whether the target has an attached client.
    canAccessOpener: bool
            Whether the target has access to the originating window.
    openerId: Optional[TargetID]
            Opener target Id
    openerFrameId: Optional[page.FrameId]
            Frame id of originating window (is only set if target has an opener).
    browserContextId: Optional[browser.BrowserContextID]
    """

    targetId: TargetID
    type: str
    title: str
    url: str
    attached: bool
    canAccessOpener: bool
    openerId: Optional[TargetID] = None
    openerFrameId: Optional[page.FrameId] = None
    browserContextId: Optional[browser.BrowserContextID] = None

    @classmethod
    def from_json(cls, json: dict) -> TargetInfo:
        return cls(
            TargetID(json["targetId"]),
            json["type"],
            json["title"],
            json["url"],
            json["attached"],
            json["canAccessOpener"],
            TargetID(json["openerId"]) if "openerId" in json else None,
            page.FrameId(json["openerFrameId"]) if "openerFrameId" in json else None,
            browser.BrowserContextID(json["browserContextId"])
            if "browserContextId" in json
            else None,
        )


@dataclasses.dataclass
class RemoteLocation:
    """
    Attributes
    ----------
    host: str
    port: int
    """

    host: str
    port: int

    @classmethod
    def from_json(cls, json: dict) -> RemoteLocation:
        return cls(json["host"], json["port"])


def activate_target(targetId: TargetID):
    """Activates (focuses) the target.

    Parameters
    ----------
    targetId: TargetID
    """
    return {"method": "Target.activateTarget", "params": {"targetId": targetId}}


def attach_to_target(targetId: TargetID, flatten: Optional[bool] = None):
    """Attaches to the target with given id.

    Parameters
    ----------
    targetId: TargetID
    flatten: Optional[bool]
            Enables "flat" access to the session via specifying sessionId attribute in the commands.
            We plan to make this the default, deprecate non-flattened mode,
            and eventually retire it. See crbug.com/991325.

    Returns
    -------
    sessionId: SessionID
            Id assigned to the session.
    """
    return filter_unset_parameters(
        {
            "method": "Target.attachToTarget",
            "params": {"targetId": targetId, "flatten": flatten},
        }
    )


def attach_to_browser_target():
    """Attaches to the browser target, only uses flat sessionId mode.

    **Experimental**

    Returns
    -------
    sessionId: SessionID
            Id assigned to the session.
    """
    return {"method": "Target.attachToBrowserTarget", "params": {}}


def close_target(targetId: TargetID):
    """Closes the target. If the target is a page that gets closed too.

    Parameters
    ----------
    targetId: TargetID

    Returns
    -------
    success: bool
            Always set to true. If an error occurs, the response indicates protocol error.
    """
    return {"method": "Target.closeTarget", "params": {"targetId": targetId}}


def expose_dev_tools_protocol(targetId: TargetID, bindingName: Optional[str] = None):
    """Inject object to the target's main frame that provides a communication
    channel with browser target.

    Injected object will be available as `window[bindingName]`.

    The object has the follwing API:
    - `binding.send(json)` - a method to send messages over the remote debugging protocol
    - `binding.onmessage = json => handleMessage(json)` - a callback that will be called for the protocol notifications and command responses.

    **Experimental**

    Parameters
    ----------
    targetId: TargetID
    bindingName: Optional[str]
            Binding name, 'cdp' if not specified.
    """
    return filter_unset_parameters(
        {
            "method": "Target.exposeDevToolsProtocol",
            "params": {"targetId": targetId, "bindingName": bindingName},
        }
    )


def create_browser_context(
    disposeOnDetach: Optional[bool] = None,
    proxyServer: Optional[str] = None,
    proxyBypassList: Optional[str] = None,
):
    """Creates a new empty BrowserContext. Similar to an incognito profile but you can have more than
    one.

    **Experimental**

    Parameters
    ----------
    disposeOnDetach: Optional[bool]
            If specified, disposes this context when debugging session disconnects.
    proxyServer: Optional[str]
            Proxy server, similar to the one passed to --proxy-server
    proxyBypassList: Optional[str]
            Proxy bypass list, similar to the one passed to --proxy-bypass-list

    Returns
    -------
    browserContextId: browser.BrowserContextID
            The id of the context created.
    """
    return filter_unset_parameters(
        {
            "method": "Target.createBrowserContext",
            "params": {
                "disposeOnDetach": disposeOnDetach,
                "proxyServer": proxyServer,
                "proxyBypassList": proxyBypassList,
            },
        }
    )


def get_browser_contexts():
    """Returns all browser contexts created with `Target.createBrowserContext` method.

    **Experimental**

    Returns
    -------
    browserContextIds: list[browser.BrowserContextID]
            An array of browser context ids.
    """
    return {"method": "Target.getBrowserContexts", "params": {}}


def create_target(
    url: str,
    width: Optional[int] = None,
    height: Optional[int] = None,
    browserContextId: Optional[browser.BrowserContextID] = None,
    enableBeginFrameControl: Optional[bool] = None,
    newWindow: Optional[bool] = None,
    background: Optional[bool] = None,
):
    """Creates a new page.

    Parameters
    ----------
    url: str
            The initial URL the page will be navigated to.
    width: Optional[int]
            Frame width in DIP (headless chrome only).
    height: Optional[int]
            Frame height in DIP (headless chrome only).
    browserContextId: Optional[browser.BrowserContextID]
            The browser context to create the page in.
    enableBeginFrameControl: Optional[bool]
            Whether BeginFrames for this target will be controlled via DevTools (headless chrome only,
            not supported on MacOS yet, false by default).
    newWindow: Optional[bool]
            Whether to create a new Window or Tab (chrome-only, false by default).
    background: Optional[bool]
            Whether to create the target in background or foreground (chrome-only,
            false by default).

    Returns
    -------
    targetId: TargetID
            The id of the page opened.
    """
    return filter_unset_parameters(
        {
            "method": "Target.createTarget",
            "params": {
                "url": url,
                "width": width,
                "height": height,
                "browserContextId": browserContextId,
                "enableBeginFrameControl": enableBeginFrameControl,
                "newWindow": newWindow,
                "background": background,
            },
        }
    )


def detach_from_target(
    sessionId: Optional[SessionID] = None, targetId: Optional[TargetID] = None
):
    """Detaches session with given id.

    Parameters
    ----------
    sessionId: Optional[SessionID]
            Session to detach.
    targetId: Optional[TargetID]
            Deprecated.
    """
    return filter_unset_parameters(
        {
            "method": "Target.detachFromTarget",
            "params": {"sessionId": sessionId, "targetId": targetId},
        }
    )


def dispose_browser_context(browserContextId: browser.BrowserContextID):
    """Deletes a BrowserContext. All the belonging pages will be closed without calling their
    beforeunload hooks.

    **Experimental**

    Parameters
    ----------
    browserContextId: browser.BrowserContextID
    """
    return {
        "method": "Target.disposeBrowserContext",
        "params": {"browserContextId": browserContextId},
    }


def get_target_info(targetId: Optional[TargetID] = None):
    """Returns information about a target.

    **Experimental**

    Parameters
    ----------
    targetId: Optional[TargetID]

    Returns
    -------
    targetInfo: TargetInfo
    """
    return filter_unset_parameters(
        {"method": "Target.getTargetInfo", "params": {"targetId": targetId}}
    )


def get_targets():
    """Retrieves a list of available targets.

    Returns
    -------
    targetInfos: list[TargetInfo]
            The list of targets.
    """
    return {"method": "Target.getTargets", "params": {}}


def send_message_to_target(
    message: str,
    sessionId: Optional[SessionID] = None,
    targetId: Optional[TargetID] = None,
):
    """Sends protocol message over session with given id.
    Consider using flat mode instead; see commands attachToTarget, setAutoAttach,
    and crbug.com/991325.

    **Deprectated**

    Parameters
    ----------
    message: str
    sessionId: Optional[SessionID]
            Identifier of the session.
    targetId: Optional[TargetID]
            Deprecated.
    """
    return filter_unset_parameters(
        {
            "method": "Target.sendMessageToTarget",
            "params": {
                "message": message,
                "sessionId": sessionId,
                "targetId": targetId,
            },
        }
    )


def set_auto_attach(
    autoAttach: bool, waitForDebuggerOnStart: bool, flatten: Optional[bool] = None
):
    """Controls whether to automatically attach to new targets which are considered to be related to
    this one. When turned on, attaches to all existing related targets as well. When turned off,
    automatically detaches from all currently attached targets.

    **Experimental**

    Parameters
    ----------
    autoAttach: bool
            Whether to auto-attach to related targets.
    waitForDebuggerOnStart: bool
            Whether to pause new targets when attaching to them. Use `Runtime.runIfWaitingForDebugger`
            to run paused targets.
    flatten: Optional[bool]
            Enables "flat" access to the session via specifying sessionId attribute in the commands.
            We plan to make this the default, deprecate non-flattened mode,
            and eventually retire it. See crbug.com/991325.
    """
    return filter_unset_parameters(
        {
            "method": "Target.setAutoAttach",
            "params": {
                "autoAttach": autoAttach,
                "waitForDebuggerOnStart": waitForDebuggerOnStart,
                "flatten": flatten,
            },
        }
    )


def set_discover_targets(discover: bool):
    """Controls whether to discover available targets and notify via
    `targetCreated/targetInfoChanged/targetDestroyed` events.

    Parameters
    ----------
    discover: bool
            Whether to discover available targets.
    """
    return {"method": "Target.setDiscoverTargets", "params": {"discover": discover}}


def set_remote_locations(locations: list[RemoteLocation]):
    """Enables target discovery for the specified locations, when `setDiscoverTargets` was set to
    `true`.

    **Experimental**

    Parameters
    ----------
    locations: list[RemoteLocation]
            List of remote locations.
    """
    return {"method": "Target.setRemoteLocations", "params": {"locations": locations}}
