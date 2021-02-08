from __future__ import annotations

import dataclasses
import enum
from typing import Optional

from . import target
from .common import Type, filter_unset_parameters


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
class Bounds(Type):
    """Browser window bounds information

    Attributes
    ----------
    left: Optional[int] = None
            The offset from the left edge of the screen to the window in pixels.
    top: Optional[int] = None
            The offset from the top edge of the screen to the window in pixels.
    width: Optional[int] = None
            The window width in pixels.
    height: Optional[int] = None
            The window height in pixels.
    windowState: Optional[WindowState] = None
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
class PermissionDescriptor(Type):
    """Definition of PermissionDescriptor defined in the Permissions API:
    https://w3c.github.io/permissions/#dictdef-permissiondescriptor.

    Attributes
    ----------
    name: str
            Name of permission.
            See https://cs.chromium.org/chromium/src/third_party/blink/renderer/modules/permissions/permission_descriptor.idl for valid permission names.
    sysex: Optional[bool] = None
            For "midi" permission, may also specify sysex control.
    userVisibleOnly: Optional[bool] = None
            For "push" permission, may specify userVisibleOnly.
            Note that userVisibleOnly = true is the only currently supported type.
    allowWithoutSanitization: Optional[bool] = None
            For "clipboard" permission, may specify allowWithoutSanitization.
    panTiltZoom: Optional[bool] = None
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


class BrowserCommandId(enum.Enum):
    """Browser command ids used by executeBrowserCommand."""

    OPEN_TAB_SEARCH = "openTabSearch"
    CLOSE_TAB_SEARCH = "closeTabSearch"


@dataclasses.dataclass
class Bucket(Type):
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


@dataclasses.dataclass
class Histogram(Type):
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
            [Bucket.from_json(x) for x in json["buckets"]],
        )


def set_permission(
    permission: PermissionDescriptor,
    setting: PermissionSetting,
    origin: Optional[str] = None,
    browserContextId: Optional[BrowserContextID] = None,
):
    """Set permission settings for given origin.

    **Experimental**

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
    """
    return filter_unset_parameters(
        {
            "method": "Browser.setPermission",
            "params": {
                "permission": permission,
                "setting": setting,
                "origin": origin,
                "browserContextId": browserContextId,
            },
        }
    )


def grant_permissions(
    permissions: list[PermissionType],
    origin: Optional[str] = None,
    browserContextId: Optional[BrowserContextID] = None,
):
    """Grant specific permissions to the given origin and reject all others.

    **Experimental**

    Parameters
    ----------
    permissions: list[PermissionType]
    origin: Optional[str]
            Origin the permission applies to, all origins if not specified.
    browserContextId: Optional[BrowserContextID]
            BrowserContext to override permissions. When omitted, default browser context is used.
    """
    return filter_unset_parameters(
        {
            "method": "Browser.grantPermissions",
            "params": {
                "permissions": permissions,
                "origin": origin,
                "browserContextId": browserContextId,
            },
        }
    )


def reset_permissions(browserContextId: Optional[BrowserContextID] = None):
    """Reset all permission management for all origins.

    **Experimental**

    Parameters
    ----------
    browserContextId: Optional[BrowserContextID]
            BrowserContext to reset permissions. When omitted, default browser context is used.
    """
    return filter_unset_parameters(
        {
            "method": "Browser.resetPermissions",
            "params": {"browserContextId": browserContextId},
        }
    )


def set_download_behavior(
    behavior: str,
    browserContextId: Optional[BrowserContextID] = None,
    downloadPath: Optional[str] = None,
):
    """Set the behavior when downloading a file.

    **Experimental**

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
    """
    return filter_unset_parameters(
        {
            "method": "Browser.setDownloadBehavior",
            "params": {
                "behavior": behavior,
                "browserContextId": browserContextId,
                "downloadPath": downloadPath,
            },
        }
    )


def close():
    """Close browser gracefully."""
    return {"method": "Browser.close", "params": {}}


def crash():
    """Crashes browser on the main thread.

    **Experimental**
    """
    return {"method": "Browser.crash", "params": {}}


def crash_gpu_process():
    """Crashes GPU process.

    **Experimental**
    """
    return {"method": "Browser.crashGpuProcess", "params": {}}


def get_version():
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
    return {"method": "Browser.getVersion", "params": {}}


def get_browser_command_line():
    """Returns the command line switches for the browser process if, and only if
    --enable-automation is on the commandline.

    **Experimental**

    Returns
    -------
    arguments: list[str]
            Commandline parameters
    """
    return {"method": "Browser.getBrowserCommandLine", "params": {}}


def get_histograms(query: Optional[str] = None, delta: Optional[bool] = None):
    """Get Chrome histograms.

    **Experimental**

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
    """
    return filter_unset_parameters(
        {"method": "Browser.getHistograms", "params": {"query": query, "delta": delta}}
    )


def get_histogram(name: str, delta: Optional[bool] = None):
    """Get a Chrome histogram by name.

    **Experimental**

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
    """
    return filter_unset_parameters(
        {"method": "Browser.getHistogram", "params": {"name": name, "delta": delta}}
    )


def get_window_bounds(windowId: WindowID):
    """Get position and size of the browser window.

    **Experimental**

    Parameters
    ----------
    windowId: WindowID
            Browser window id.

    Returns
    -------
    bounds: Bounds
            Bounds information of the window. When window state is 'minimized', the restored window
            position and size are returned.
    """
    return {"method": "Browser.getWindowBounds", "params": {"windowId": windowId}}


def get_window_for_target(targetId: Optional[target.TargetID] = None):
    """Get the browser window that contains the devtools target.

    **Experimental**

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
    """
    return filter_unset_parameters(
        {"method": "Browser.getWindowForTarget", "params": {"targetId": targetId}}
    )


def set_window_bounds(windowId: WindowID, bounds: Bounds):
    """Set position and/or size of the browser window.

    **Experimental**

    Parameters
    ----------
    windowId: WindowID
            Browser window id.
    bounds: Bounds
            New window bounds. The 'minimized', 'maximized' and 'fullscreen' states cannot be combined
            with 'left', 'top', 'width' or 'height'. Leaves unspecified fields unchanged.
    """
    return {
        "method": "Browser.setWindowBounds",
        "params": {"windowId": windowId, "bounds": bounds},
    }


def set_dock_tile(badgeLabel: Optional[str] = None, image: Optional[str] = None):
    """Set dock tile details, platform-specific.

    **Experimental**

    Parameters
    ----------
    badgeLabel: Optional[str]
    image: Optional[str]
            Png encoded image. (Encoded as a base64 string when passed over JSON)
    """
    return filter_unset_parameters(
        {
            "method": "Browser.setDockTile",
            "params": {"badgeLabel": badgeLabel, "image": image},
        }
    )


def execute_browser_command(commandId: BrowserCommandId):
    """Invoke custom browser commands used by telemetry.

    **Experimental**

    Parameters
    ----------
    commandId: BrowserCommandId
    """
    return {
        "method": "Browser.executeBrowserCommand",
        "params": {"commandId": commandId},
    }
