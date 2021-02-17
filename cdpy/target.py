from __future__ import annotations

import dataclasses
from typing import Generator, Optional

from deprecated.sphinx import deprecated

from . import browser, page
from .common import filter_none


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

    def to_json(self) -> dict:
        return filter_none(
            {
                "targetId": str(self.targetId),
                "type": self.type,
                "title": self.title,
                "url": self.url,
                "attached": self.attached,
                "canAccessOpener": self.canAccessOpener,
                "openerId": str(self.openerId) if self.openerId else None,
                "openerFrameId": str(self.openerFrameId)
                if self.openerFrameId
                else None,
                "browserContextId": str(self.browserContextId)
                if self.browserContextId
                else None,
            }
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

    def to_json(self) -> dict:
        return {"host": self.host, "port": self.port}


def activate_target(targetId: TargetID) -> dict:
    """Activates (focuses) the target.

    Parameters
    ----------
    targetId: TargetID
    """
    return {"method": "Target.activateTarget", "params": {"targetId": str(targetId)}}


def attach_to_target(
    targetId: TargetID, flatten: Optional[bool] = None
) -> Generator[dict, dict, SessionID]:
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
    response = yield {
        "method": "Target.attachToTarget",
        "params": filter_none({"targetId": str(targetId), "flatten": flatten}),
    }
    return SessionID(response["sessionId"])


def attach_to_browser_target() -> Generator[dict, dict, SessionID]:
    """Attaches to the browser target, only uses flat sessionId mode.

    Returns
    -------
    sessionId: SessionID
            Id assigned to the session.

    **Experimental**
    """
    response = yield {"method": "Target.attachToBrowserTarget", "params": {}}
    return SessionID(response["sessionId"])


def close_target(targetId: TargetID) -> Generator[dict, dict, bool]:
    """Closes the target. If the target is a page that gets closed too.

    Parameters
    ----------
    targetId: TargetID

    Returns
    -------
    success: bool
            Always set to true. If an error occurs, the response indicates protocol error.
    """
    response = yield {
        "method": "Target.closeTarget",
        "params": {"targetId": str(targetId)},
    }
    return response["success"]


def expose_dev_tools_protocol(
    targetId: TargetID, bindingName: Optional[str] = None
) -> dict:
    """Inject object to the target's main frame that provides a communication
    channel with browser target.

    Injected object will be available as `window[bindingName]`.

    The object has the follwing API:
    - `binding.send(json)` - a method to send messages over the remote debugging protocol
    - `binding.onmessage = json => handleMessage(json)` - a callback that will be called for the protocol notifications and command responses.

    Parameters
    ----------
    targetId: TargetID
    bindingName: Optional[str]
            Binding name, 'cdp' if not specified.

    **Experimental**
    """
    return {
        "method": "Target.exposeDevToolsProtocol",
        "params": filter_none({"targetId": str(targetId), "bindingName": bindingName}),
    }


def create_browser_context(
    disposeOnDetach: Optional[bool] = None,
    proxyServer: Optional[str] = None,
    proxyBypassList: Optional[str] = None,
) -> Generator[dict, dict, browser.BrowserContextID]:
    """Creates a new empty BrowserContext. Similar to an incognito profile but you can have more than
    one.

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

    **Experimental**
    """
    response = yield {
        "method": "Target.createBrowserContext",
        "params": filter_none(
            {
                "disposeOnDetach": disposeOnDetach,
                "proxyServer": proxyServer,
                "proxyBypassList": proxyBypassList,
            }
        ),
    }
    return browser.BrowserContextID(response["browserContextId"])


def get_browser_contexts() -> Generator[dict, dict, list[browser.BrowserContextID]]:
    """Returns all browser contexts created with `Target.createBrowserContext` method.

    Returns
    -------
    browserContextIds: list[browser.BrowserContextID]
            An array of browser context ids.

    **Experimental**
    """
    response = yield {"method": "Target.getBrowserContexts", "params": {}}
    return [browser.BrowserContextID(b) for b in response["browserContextIds"]]


def create_target(
    url: str,
    width: Optional[int] = None,
    height: Optional[int] = None,
    browserContextId: Optional[browser.BrowserContextID] = None,
    enableBeginFrameControl: Optional[bool] = None,
    newWindow: Optional[bool] = None,
    background: Optional[bool] = None,
) -> Generator[dict, dict, TargetID]:
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
    response = yield {
        "method": "Target.createTarget",
        "params": filter_none(
            {
                "url": url,
                "width": width,
                "height": height,
                "browserContextId": str(browserContextId) if browserContextId else None,
                "enableBeginFrameControl": enableBeginFrameControl,
                "newWindow": newWindow,
                "background": background,
            }
        ),
    }
    return TargetID(response["targetId"])


def detach_from_target(
    sessionId: Optional[SessionID] = None, targetId: Optional[TargetID] = None
) -> dict:
    """Detaches session with given id.

    Parameters
    ----------
    sessionId: Optional[SessionID]
            Session to detach.
    targetId: Optional[TargetID]
            Deprecated.
    """
    return {
        "method": "Target.detachFromTarget",
        "params": filter_none(
            {
                "sessionId": str(sessionId) if sessionId else None,
                "targetId": str(targetId) if targetId else None,
            }
        ),
    }


def dispose_browser_context(browserContextId: browser.BrowserContextID) -> dict:
    """Deletes a BrowserContext. All the belonging pages will be closed without calling their
    beforeunload hooks.

    Parameters
    ----------
    browserContextId: browser.BrowserContextID

    **Experimental**
    """
    return {
        "method": "Target.disposeBrowserContext",
        "params": {"browserContextId": str(browserContextId)},
    }


def get_target_info(
    targetId: Optional[TargetID] = None,
) -> Generator[dict, dict, TargetInfo]:
    """Returns information about a target.

    Parameters
    ----------
    targetId: Optional[TargetID]

    Returns
    -------
    targetInfo: TargetInfo

    **Experimental**
    """
    response = yield {
        "method": "Target.getTargetInfo",
        "params": filter_none({"targetId": str(targetId) if targetId else None}),
    }
    return TargetInfo.from_json(response["targetInfo"])


def get_targets() -> Generator[dict, dict, list[TargetInfo]]:
    """Retrieves a list of available targets.

    Returns
    -------
    targetInfos: list[TargetInfo]
            The list of targets.
    """
    response = yield {"method": "Target.getTargets", "params": {}}
    return [TargetInfo.from_json(t) for t in response["targetInfos"]]


@deprecated(version=1.3)
def send_message_to_target(
    message: str,
    sessionId: Optional[SessionID] = None,
    targetId: Optional[TargetID] = None,
) -> dict:
    """Sends protocol message over session with given id.
    Consider using flat mode instead; see commands attachToTarget, setAutoAttach,
    and crbug.com/991325.

    Parameters
    ----------
    message: str
    sessionId: Optional[SessionID]
            Identifier of the session.
    targetId: Optional[TargetID]
            Deprecated.
    """
    return {
        "method": "Target.sendMessageToTarget",
        "params": filter_none(
            {
                "message": message,
                "sessionId": str(sessionId) if sessionId else None,
                "targetId": str(targetId) if targetId else None,
            }
        ),
    }


def set_auto_attach(
    autoAttach: bool, waitForDebuggerOnStart: bool, flatten: Optional[bool] = None
) -> dict:
    """Controls whether to automatically attach to new targets which are considered to be related to
    this one. When turned on, attaches to all existing related targets as well. When turned off,
    automatically detaches from all currently attached targets.

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

    **Experimental**
    """
    return {
        "method": "Target.setAutoAttach",
        "params": filter_none(
            {
                "autoAttach": autoAttach,
                "waitForDebuggerOnStart": waitForDebuggerOnStart,
                "flatten": flatten,
            }
        ),
    }


def set_discover_targets(discover: bool) -> dict:
    """Controls whether to discover available targets and notify via
    `targetCreated/targetInfoChanged/targetDestroyed` events.

    Parameters
    ----------
    discover: bool
            Whether to discover available targets.
    """
    return {"method": "Target.setDiscoverTargets", "params": {"discover": discover}}


def set_remote_locations(locations: list[RemoteLocation]) -> dict:
    """Enables target discovery for the specified locations, when `setDiscoverTargets` was set to
    `true`.

    Parameters
    ----------
    locations: list[RemoteLocation]
            List of remote locations.

    **Experimental**
    """
    return {
        "method": "Target.setRemoteLocations",
        "params": {"locations": [l.to_json() for l in locations]},
    }


@dataclasses.dataclass
class AttachedToTarget:
    """Issued when attached to target because of auto-attach or `attachToTarget` command.

    Attributes
    ----------
    sessionId: SessionID
            Identifier assigned to the session used to send/receive messages.
    targetInfo: TargetInfo
    waitingForDebugger: bool
    """

    sessionId: SessionID
    targetInfo: TargetInfo
    waitingForDebugger: bool

    @classmethod
    def from_json(cls, json: dict) -> AttachedToTarget:
        return cls(
            SessionID(json["sessionId"]),
            TargetInfo.from_json(json["targetInfo"]),
            json["waitingForDebugger"],
        )


@dataclasses.dataclass
class DetachedFromTarget:
    """Issued when detached from target for any reason (including `detachFromTarget` command). Can be
    issued multiple times per target if multiple sessions have been attached to it.

    Attributes
    ----------
    sessionId: SessionID
            Detached session identifier.
    targetId: Optional[TargetID]
            Deprecated.
    """

    sessionId: SessionID
    targetId: Optional[TargetID] = None

    @classmethod
    def from_json(cls, json: dict) -> DetachedFromTarget:
        return cls(
            SessionID(json["sessionId"]),
            TargetID(json["targetId"]) if "targetId" in json else None,
        )


@dataclasses.dataclass
class ReceivedMessageFromTarget:
    """Notifies about a new protocol message received from the session (as reported in
    `attachedToTarget` event).

    Attributes
    ----------
    sessionId: SessionID
            Identifier of a session which sends a message.
    message: str
    targetId: Optional[TargetID]
            Deprecated.
    """

    sessionId: SessionID
    message: str
    targetId: Optional[TargetID] = None

    @classmethod
    def from_json(cls, json: dict) -> ReceivedMessageFromTarget:
        return cls(
            SessionID(json["sessionId"]),
            json["message"],
            TargetID(json["targetId"]) if "targetId" in json else None,
        )


@dataclasses.dataclass
class TargetCreated:
    """Issued when a possible inspection target is created.

    Attributes
    ----------
    targetInfo: TargetInfo
    """

    targetInfo: TargetInfo

    @classmethod
    def from_json(cls, json: dict) -> TargetCreated:
        return cls(TargetInfo.from_json(json["targetInfo"]))


@dataclasses.dataclass
class TargetDestroyed:
    """Issued when a target is destroyed.

    Attributes
    ----------
    targetId: TargetID
    """

    targetId: TargetID

    @classmethod
    def from_json(cls, json: dict) -> TargetDestroyed:
        return cls(TargetID(json["targetId"]))


@dataclasses.dataclass
class TargetCrashed:
    """Issued when a target has crashed.

    Attributes
    ----------
    targetId: TargetID
    status: str
            Termination status type.
    errorCode: int
            Termination error code.
    """

    targetId: TargetID
    status: str
    errorCode: int

    @classmethod
    def from_json(cls, json: dict) -> TargetCrashed:
        return cls(TargetID(json["targetId"]), json["status"], json["errorCode"])


@dataclasses.dataclass
class TargetInfoChanged:
    """Issued when some information about a target has changed. This only happens between
    `targetCreated` and `targetDestroyed`.

    Attributes
    ----------
    targetInfo: TargetInfo
    """

    targetInfo: TargetInfo

    @classmethod
    def from_json(cls, json: dict) -> TargetInfoChanged:
        return cls(TargetInfo.from_json(json["targetInfo"]))
