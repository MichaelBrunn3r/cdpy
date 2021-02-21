from __future__ import annotations

import dataclasses
import enum
from typing import Generator, Optional

from . import target
from ._utils import filter_none


class BrowserContextID(str):
    """"""

    def __repr__(self):
        return f"BrowserContextID({super().__repr__()})"


class WindowID(int):
    """"""

    def __repr__(self):
        return f"WindowID({super().__repr__()})"


class WindowState(enum.Enum):
    """The state of the browser window."""

    NORMAL = "normal"
    MINIMIZED = "minimized"
    MAXIMIZED = "maximized"
    FULLSCREEN = "fullscreen"


@dataclasses.dataclass
class Bounds:
    """Browser window bounds information

    Attributes
    ----------
    left: Optional[int]
            The offset from the left edge of the screen to the window in pixels.
    top: Optional[int]
            The offset from the top edge of the screen to the window in pixels.
    width: Optional[int]
            The window width in pixels.
    height: Optional[int]
            The window height in pixels.
    windowState: Optional[WindowState]
            The window state. Default to normal.
    """

    left: Optional[int] = None
    top: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    windowState: Optional[WindowState] = None

    @classmethod
    def from_json(cls, json: dict) -> Bounds:
        return cls(
            json.get("left"),
            json.get("top"),
            json.get("width"),
            json.get("height"),
            WindowState(json["windowState"]) if "windowState" in json else None,
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "left": self.left,
                "top": self.top,
                "width": self.width,
                "height": self.height,
                "windowState": self.windowState.value if self.windowState else None,
            }
        )


class PermissionType(enum.Enum):
    """"""

    ACCESSIBILITY_EVENTS = "accessibilityEvents"
    AUDIO_CAPTURE = "audioCapture"
    BACKGROUND_SYNC = "backgroundSync"
    BACKGROUND_FETCH = "backgroundFetch"
    CLIPBOARD_READ_WRITE = "clipboardReadWrite"
    CLIPBOARD_SANITIZED_WRITE = "clipboardSanitizedWrite"
    DISPLAY_CAPTURE = "displayCapture"
    DURABLE_STORAGE = "durableStorage"
    FLASH = "flash"
    GEOLOCATION = "geolocation"
    MIDI = "midi"
    MIDI_SYSEX = "midiSysex"
    NFC = "nfc"
    NOTIFICATIONS = "notifications"
    PAYMENT_HANDLER = "paymentHandler"
    PERIODIC_BACKGROUND_SYNC = "periodicBackgroundSync"
    PROTECTED_MEDIA_IDENTIFIER = "protectedMediaIdentifier"
    SENSORS = "sensors"
    VIDEO_CAPTURE = "videoCapture"
    VIDEO_CAPTURE_PAN_TILT_ZOOM = "videoCapturePanTiltZoom"
    IDLE_DETECTION = "idleDetection"
    WAKE_LOCK_SCREEN = "wakeLockScreen"
    WAKE_LOCK_SYSTEM = "wakeLockSystem"


class PermissionSetting(enum.Enum):
    """"""

    GRANTED = "granted"
    DENIED = "denied"
    PROMPT = "prompt"


@dataclasses.dataclass
class PermissionDescriptor:
    """Definition of PermissionDescriptor defined in the Permissions API:
    https://w3c.github.io/permissions/#dictdef-permissiondescriptor.

    Attributes
    ----------
    name: str
            Name of permission.
            See https://cs.chromium.org/chromium/src/third_party/blink/renderer/modules/permissions/permission_descriptor.idl for valid permission names.
    sysex: Optional[bool]
            For "midi" permission, may also specify sysex control.
    userVisibleOnly: Optional[bool]
            For "push" permission, may specify userVisibleOnly.
            Note that userVisibleOnly = true is the only currently supported type.
    allowWithoutSanitization: Optional[bool]
            For "clipboard" permission, may specify allowWithoutSanitization.
    panTiltZoom: Optional[bool]
            For "camera" permission, may specify panTiltZoom.
    """

    name: str
    sysex: Optional[bool] = None
    userVisibleOnly: Optional[bool] = None
    allowWithoutSanitization: Optional[bool] = None
    panTiltZoom: Optional[bool] = None

    @classmethod
    def from_json(cls, json: dict) -> PermissionDescriptor:
        return cls(
            json["name"],
            json.get("sysex"),
            json.get("userVisibleOnly"),
            json.get("allowWithoutSanitization"),
            json.get("panTiltZoom"),
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "name": self.name,
                "sysex": self.sysex,
                "userVisibleOnly": self.userVisibleOnly,
                "allowWithoutSanitization": self.allowWithoutSanitization,
                "panTiltZoom": self.panTiltZoom,
            }
        )


class BrowserCommandId(enum.Enum):
    """Browser command ids used by executeBrowserCommand."""

    OPEN_TAB_SEARCH = "openTabSearch"
    CLOSE_TAB_SEARCH = "closeTabSearch"


@dataclasses.dataclass
class Bucket:
    """Chrome histogram bucket.

    Attributes
    ----------
    low: int
            Minimum value (inclusive).
    high: int
            Maximum value (exclusive).
    count: int
            Number of samples.
    """

    low: int
    high: int
    count: int

    @classmethod
    def from_json(cls, json: dict) -> Bucket:
        return cls(json["low"], json["high"], json["count"])

    def to_json(self) -> dict:
        return {"low": self.low, "high": self.high, "count": self.count}


@dataclasses.dataclass
class Histogram:
    """Chrome histogram.

    Attributes
    ----------
    name: str
            Name.
    sum: int
            Sum of sample values.
    count: int
            Total number of samples.
    buckets: list[Bucket]
            Buckets.
    """

    name: str
    sum: int
    count: int
    buckets: list[Bucket]

    @classmethod
    def from_json(cls, json: dict) -> Histogram:
        return cls(
            json["name"],
            json["sum"],
            json["count"],
            [Bucket.from_json(b) for b in json["buckets"]],
        )

    def to_json(self) -> dict:
        return {
            "name": self.name,
            "sum": self.sum,
            "count": self.count,
            "buckets": [b.to_json() for b in self.buckets],
        }


def set_permission(
    permission: PermissionDescriptor,
    setting: PermissionSetting,
    origin: Optional[str] = None,
    browserContextId: Optional[BrowserContextID] = None,
) -> dict:
    """Set permission settings for given origin.

    Parameters
    ----------
    permission: PermissionDescriptor
            Descriptor of permission to override.
    setting: PermissionSetting
            Setting of the permission.
    origin: Optional[str]
            Origin the permission applies to, all origins if not specified.
    browserContextId: Optional[BrowserContextID]
            Context to override. When omitted, default browser context is used.

    **Experimental**
    """
    return {
        "method": "Browser.setPermission",
        "params": filter_none(
            {
                "permission": permission.to_json(),
                "setting": setting.value,
                "origin": origin,
                "browserContextId": str(browserContextId) if browserContextId else None,
            }
        ),
    }


def grant_permissions(
    permissions: list[PermissionType],
    origin: Optional[str] = None,
    browserContextId: Optional[BrowserContextID] = None,
) -> dict:
    """Grant specific permissions to the given origin and reject all others.

    Parameters
    ----------
    permissions: list[PermissionType]
    origin: Optional[str]
            Origin the permission applies to, all origins if not specified.
    browserContextId: Optional[BrowserContextID]
            BrowserContext to override permissions. When omitted, default browser context is used.

    **Experimental**
    """
    return {
        "method": "Browser.grantPermissions",
        "params": filter_none(
            {
                "permissions": [p.value for p in permissions],
                "origin": origin,
                "browserContextId": str(browserContextId) if browserContextId else None,
            }
        ),
    }


def reset_permissions(browserContextId: Optional[BrowserContextID] = None) -> dict:
    """Reset all permission management for all origins.

    Parameters
    ----------
    browserContextId: Optional[BrowserContextID]
            BrowserContext to reset permissions. When omitted, default browser context is used.

    **Experimental**
    """
    return {
        "method": "Browser.resetPermissions",
        "params": filter_none(
            {"browserContextId": str(browserContextId) if browserContextId else None}
        ),
    }


def set_download_behavior(
    behavior: str,
    browserContextId: Optional[BrowserContextID] = None,
    downloadPath: Optional[str] = None,
) -> dict:
    """Set the behavior when downloading a file.

    Parameters
    ----------
    behavior: str
            Whether to allow all or deny all download requests, or use default Chrome behavior if
            available (otherwise deny). |allowAndName| allows download and names files according to
            their dowmload guids.
    browserContextId: Optional[BrowserContextID]
            BrowserContext to set download behavior. When omitted, default browser context is used.
    downloadPath: Optional[str]
            The default path to save downloaded files to. This is requred if behavior is set to 'allow'
            or 'allowAndName'.

    **Experimental**
    """
    return {
        "method": "Browser.setDownloadBehavior",
        "params": filter_none(
            {
                "behavior": behavior,
                "browserContextId": str(browserContextId) if browserContextId else None,
                "downloadPath": downloadPath,
            }
        ),
    }


def close() -> dict:
    """Close browser gracefully."""
    return {"method": "Browser.close", "params": {}}


def crash() -> dict:
    """Crashes browser on the main thread.

    **Experimental**
    """
    return {"method": "Browser.crash", "params": {}}


def crash_gpu_process() -> dict:
    """Crashes GPU process.

    **Experimental**
    """
    return {"method": "Browser.crashGpuProcess", "params": {}}


def get_version() -> Generator[dict, dict, dict]:
    """Returns version information.

    Returns
    -------
    protocolVersion: str
            Protocol version.
    product: str
            Product name.
    revision: str
            Product revision.
    userAgent: str
            User-Agent.
    jsVersion: str
            V8 version.
    """
    response = yield {"method": "Browser.getVersion", "params": {}}
    return {
        "protocolVersion": response["protocolVersion"],
        "product": response["product"],
        "revision": response["revision"],
        "userAgent": response["userAgent"],
        "jsVersion": response["jsVersion"],
    }


def get_browser_command_line() -> Generator[dict, dict, list[str]]:
    """Returns the command line switches for the browser process if, and only if
    --enable-automation is on the commandline.

    Returns
    -------
    arguments: list[str]
            Commandline parameters

    **Experimental**
    """
    response = yield {"method": "Browser.getBrowserCommandLine", "params": {}}
    return response["arguments"]


def get_histograms(
    query: Optional[str] = None, delta: Optional[bool] = None
) -> Generator[dict, dict, list[Histogram]]:
    """Get Chrome histograms.

    Parameters
    ----------
    query: Optional[str]
            Requested substring in name. Only histograms which have query as a
            substring in their name are extracted. An empty or absent query returns
            all histograms.
    delta: Optional[bool]
            If true, retrieve delta since last call.

    Returns
    -------
    histograms: list[Histogram]
            Histograms.

    **Experimental**
    """
    response = yield {
        "method": "Browser.getHistograms",
        "params": filter_none({"query": query, "delta": delta}),
    }
    return [Histogram.from_json(h) for h in response["histograms"]]


def get_histogram(
    name: str, delta: Optional[bool] = None
) -> Generator[dict, dict, Histogram]:
    """Get a Chrome histogram by name.

    Parameters
    ----------
    name: str
            Requested histogram name.
    delta: Optional[bool]
            If true, retrieve delta since last call.

    Returns
    -------
    histogram: Histogram
            Histogram.

    **Experimental**
    """
    response = yield {
        "method": "Browser.getHistogram",
        "params": filter_none({"name": name, "delta": delta}),
    }
    return Histogram.from_json(response["histogram"])


def get_window_bounds(windowId: WindowID) -> Generator[dict, dict, Bounds]:
    """Get position and size of the browser window.

    Parameters
    ----------
    windowId: WindowID
            Browser window id.

    Returns
    -------
    bounds: Bounds
            Bounds information of the window. When window state is 'minimized', the restored window
            position and size are returned.

    **Experimental**
    """
    response = yield {
        "method": "Browser.getWindowBounds",
        "params": {"windowId": int(windowId)},
    }
    return Bounds.from_json(response["bounds"])


def get_window_for_target(
    targetId: Optional[target.TargetID] = None,
) -> Generator[dict, dict, dict]:
    """Get the browser window that contains the devtools target.

    Parameters
    ----------
    targetId: Optional[target.TargetID]
            Devtools agent host id. If called as a part of the session, associated targetId is used.

    Returns
    -------
    windowId: WindowID
            Browser window id.
    bounds: Bounds
            Bounds information of the window. When window state is 'minimized', the restored window
            position and size are returned.

    **Experimental**
    """
    response = yield {
        "method": "Browser.getWindowForTarget",
        "params": filter_none({"targetId": str(targetId) if targetId else None}),
    }
    return {
        "windowId": WindowID(response["windowId"]),
        "bounds": Bounds.from_json(response["bounds"]),
    }


def set_window_bounds(windowId: WindowID, bounds: Bounds) -> dict:
    """Set position and/or size of the browser window.

    Parameters
    ----------
    windowId: WindowID
            Browser window id.
    bounds: Bounds
            New window bounds. The 'minimized', 'maximized' and 'fullscreen' states cannot be combined
            with 'left', 'top', 'width' or 'height'. Leaves unspecified fields unchanged.

    **Experimental**
    """
    return {
        "method": "Browser.setWindowBounds",
        "params": {"windowId": int(windowId), "bounds": bounds.to_json()},
    }


def set_dock_tile(
    badgeLabel: Optional[str] = None, image: Optional[str] = None
) -> dict:
    """Set dock tile details, platform-specific.

    Parameters
    ----------
    badgeLabel: Optional[str]
    image: Optional[str]
            Png encoded image. (Encoded as a base64 string when passed over JSON)

    **Experimental**
    """
    return {
        "method": "Browser.setDockTile",
        "params": filter_none({"badgeLabel": badgeLabel, "image": image}),
    }


def execute_browser_command(commandId: BrowserCommandId) -> dict:
    """Invoke custom browser commands used by telemetry.

    Parameters
    ----------
    commandId: BrowserCommandId

    **Experimental**
    """
    return {
        "method": "Browser.executeBrowserCommand",
        "params": {"commandId": commandId.value},
    }
