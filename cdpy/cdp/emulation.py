from __future__ import annotations

import dataclasses
import enum
from typing import Generator, Optional

from deprecated.sphinx import deprecated

from . import dom, network, page
from ._utils import filter_none


@dataclasses.dataclass
class ScreenOrientation:
    """Screen orientation.

    Attributes
    ----------
    type: str
            Orientation type.
    angle: int
            Orientation angle.
    """

    type: str
    angle: int

    @classmethod
    def from_json(cls, json: dict) -> ScreenOrientation:
        return cls(json["type"], json["angle"])

    def to_json(self) -> dict:
        return {"type": self.type, "angle": self.angle}


@dataclasses.dataclass
class DisplayFeature:
    """
    Attributes
    ----------
    orientation: str
            Orientation of a display feature in relation to screen
    offset: int
            The offset from the screen origin in either the x (for vertical
            orientation) or y (for horizontal orientation) direction.
    maskLength: int
            A display feature may mask content such that it is not physically
            displayed - this length along with the offset describes this area.
            A display feature that only splits content will have a 0 mask_length.
    """

    orientation: str
    offset: int
    maskLength: int

    @classmethod
    def from_json(cls, json: dict) -> DisplayFeature:
        return cls(json["orientation"], json["offset"], json["maskLength"])

    def to_json(self) -> dict:
        return {
            "orientation": self.orientation,
            "offset": self.offset,
            "maskLength": self.maskLength,
        }


@dataclasses.dataclass
class MediaFeature:
    """
    Attributes
    ----------
    name: str
    value: str
    """

    name: str
    value: str

    @classmethod
    def from_json(cls, json: dict) -> MediaFeature:
        return cls(json["name"], json["value"])

    def to_json(self) -> dict:
        return {"name": self.name, "value": self.value}


class VirtualTimePolicy(enum.Enum):
    """advance: If the scheduler runs out of immediate work, the virtual time base may fast forward to
    allow the next delayed task (if any) to run; pause: The virtual time base may not advance;
    pauseIfNetworkFetchesPending: The virtual time base may not advance if there are any pending
    resource fetches.
    """

    ADVANCE = "advance"
    PAUSE = "pause"
    PAUSE_IF_NETWORK_FETCHES_PENDING = "pauseIfNetworkFetchesPending"


@dataclasses.dataclass
class UserAgentBrandVersion:
    """Used to specify User Agent Cient Hints to emulate. See https://wicg.github.io/ua-client-hints

    Attributes
    ----------
    brand: str
    version: str
    """

    brand: str
    version: str

    @classmethod
    def from_json(cls, json: dict) -> UserAgentBrandVersion:
        return cls(json["brand"], json["version"])

    def to_json(self) -> dict:
        return {"brand": self.brand, "version": self.version}


@dataclasses.dataclass
class UserAgentMetadata:
    """Used to specify User Agent Cient Hints to emulate. See https://wicg.github.io/ua-client-hints
    Missing optional values will be filled in by the target with what it would normally use.

    Attributes
    ----------
    platform: str
    platformVersion: str
    architecture: str
    model: str
    mobile: bool
    brands: Optional[list[UserAgentBrandVersion]]
    fullVersion: Optional[str]
    """

    platform: str
    platformVersion: str
    architecture: str
    model: str
    mobile: bool
    brands: Optional[list[UserAgentBrandVersion]] = None
    fullVersion: Optional[str] = None

    @classmethod
    def from_json(cls, json: dict) -> UserAgentMetadata:
        return cls(
            json["platform"],
            json["platformVersion"],
            json["architecture"],
            json["model"],
            json["mobile"],
            [UserAgentBrandVersion.from_json(b) for b in json["brands"]]
            if "brands" in json
            else None,
            json.get("fullVersion"),
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "platform": self.platform,
                "platformVersion": self.platformVersion,
                "architecture": self.architecture,
                "model": self.model,
                "mobile": self.mobile,
                "brands": [b.to_json() for b in self.brands] if self.brands else None,
                "fullVersion": self.fullVersion,
            }
        )


class DisabledImageType(enum.Enum):
    """Enum of image types that can be disabled."""

    AVIF = "avif"
    WEBP = "webp"


def can_emulate() -> Generator[dict, dict, bool]:
    """Tells whether emulation is supported.

    Returns
    -------
    result: bool
            True if emulation is supported.
    """
    response = yield {"method": "Emulation.canEmulate", "params": {}}
    return response["result"]


def clear_device_metrics_override() -> dict:
    """Clears the overriden device metrics."""
    return {"method": "Emulation.clearDeviceMetricsOverride", "params": {}}


def clear_geolocation_override() -> dict:
    """Clears the overriden Geolocation Position and Error."""
    return {"method": "Emulation.clearGeolocationOverride", "params": {}}


def reset_page_scale_factor() -> dict:
    """Requests that page scale factor is reset to initial values.

    **Experimental**
    """
    return {"method": "Emulation.resetPageScaleFactor", "params": {}}


def set_focus_emulation_enabled(enabled: bool) -> dict:
    """Enables or disables simulating a focused and active page.

    Parameters
    ----------
    enabled: bool
            Whether to enable to disable focus emulation.

    **Experimental**
    """
    return {
        "method": "Emulation.setFocusEmulationEnabled",
        "params": {"enabled": enabled},
    }


def set_cpu_throttling_rate(rate: float) -> dict:
    """Enables CPU throttling to emulate slow CPUs.

    Parameters
    ----------
    rate: float
            Throttling rate as a slowdown factor (1 is no throttle, 2 is 2x slowdown, etc).

    **Experimental**
    """
    return {"method": "Emulation.setCPUThrottlingRate", "params": {"rate": rate}}


def set_default_background_color_override(color: Optional[dom.RGBA] = None) -> dict:
    """Sets or clears an override of the default background color of the frame. This override is used
    if the content does not specify one.

    Parameters
    ----------
    color: Optional[dom.RGBA]
            RGBA of the default background color. If not specified, any existing override will be
            cleared.
    """
    return {
        "method": "Emulation.setDefaultBackgroundColorOverride",
        "params": filter_none({"color": color.to_json() if color else None}),
    }


def set_device_metrics_override(
    width: int,
    height: int,
    deviceScaleFactor: float,
    mobile: bool,
    scale: Optional[float] = None,
    screenWidth: Optional[int] = None,
    screenHeight: Optional[int] = None,
    positionX: Optional[int] = None,
    positionY: Optional[int] = None,
    dontSetVisibleSize: Optional[bool] = None,
    screenOrientation: Optional[ScreenOrientation] = None,
    viewport: Optional[page.Viewport] = None,
    displayFeature: Optional[DisplayFeature] = None,
) -> dict:
    """Overrides the values of device screen dimensions (window.screen.width, window.screen.height,
    window.innerWidth, window.innerHeight, and "device-width"/"device-height"-related CSS media
    query results).

    Parameters
    ----------
    width: int
            Overriding width value in pixels (minimum 0, maximum 10000000). 0 disables the override.
    height: int
            Overriding height value in pixels (minimum 0, maximum 10000000). 0 disables the override.
    deviceScaleFactor: float
            Overriding device scale factor value. 0 disables the override.
    mobile: bool
            Whether to emulate mobile device. This includes viewport meta tag, overlay scrollbars, text
            autosizing and more.
    scale: Optional[float]
            Scale to apply to resulting view image.
    screenWidth: Optional[int]
            Overriding screen width value in pixels (minimum 0, maximum 10000000).
    screenHeight: Optional[int]
            Overriding screen height value in pixels (minimum 0, maximum 10000000).
    positionX: Optional[int]
            Overriding view X position on screen in pixels (minimum 0, maximum 10000000).
    positionY: Optional[int]
            Overriding view Y position on screen in pixels (minimum 0, maximum 10000000).
    dontSetVisibleSize: Optional[bool]
            Do not set visible view size, rely upon explicit setVisibleSize call.
    screenOrientation: Optional[ScreenOrientation]
            Screen orientation override.
    viewport: Optional[page.Viewport]
            If set, the visible area of the page will be overridden to this viewport. This viewport
            change is not observed by the page, e.g. viewport-relative elements do not change positions.
    displayFeature: Optional[DisplayFeature]
            If set, the display feature of a multi-segment screen. If not set, multi-segment support
            is turned-off.
    """
    return {
        "method": "Emulation.setDeviceMetricsOverride",
        "params": filter_none(
            {
                "width": width,
                "height": height,
                "deviceScaleFactor": deviceScaleFactor,
                "mobile": mobile,
                "scale": scale,
                "screenWidth": screenWidth,
                "screenHeight": screenHeight,
                "positionX": positionX,
                "positionY": positionY,
                "dontSetVisibleSize": dontSetVisibleSize,
                "screenOrientation": screenOrientation.to_json()
                if screenOrientation
                else None,
                "viewport": viewport.to_json() if viewport else None,
                "displayFeature": displayFeature.to_json() if displayFeature else None,
            }
        ),
    }


def set_scrollbars_hidden(hidden: bool) -> dict:
    """
    Parameters
    ----------
    hidden: bool
            Whether scrollbars should be always hidden.

    **Experimental**
    """
    return {"method": "Emulation.setScrollbarsHidden", "params": {"hidden": hidden}}


def set_document_cookie_disabled(disabled: bool) -> dict:
    """
    Parameters
    ----------
    disabled: bool
            Whether document.coookie API should be disabled.

    **Experimental**
    """
    return {
        "method": "Emulation.setDocumentCookieDisabled",
        "params": {"disabled": disabled},
    }


def set_emit_touch_events_for_mouse(
    enabled: bool, configuration: Optional[str] = None
) -> dict:
    """
    Parameters
    ----------
    enabled: bool
            Whether touch emulation based on mouse input should be enabled.
    configuration: Optional[str]
            Touch/gesture events configuration. Default: current platform.

    **Experimental**
    """
    return {
        "method": "Emulation.setEmitTouchEventsForMouse",
        "params": filter_none({"enabled": enabled, "configuration": configuration}),
    }


def set_emulated_media(
    media: Optional[str] = None, features: Optional[list[MediaFeature]] = None
) -> dict:
    """Emulates the given media type or media feature for CSS media queries.

    Parameters
    ----------
    media: Optional[str]
            Media type to emulate. Empty string disables the override.
    features: Optional[list[MediaFeature]]
            Media features to emulate.
    """
    return {
        "method": "Emulation.setEmulatedMedia",
        "params": filter_none(
            {
                "media": media,
                "features": [f.to_json() for f in features] if features else None,
            }
        ),
    }


def set_emulated_vision_deficiency(type: str) -> dict:
    """Emulates the given vision deficiency.

    Parameters
    ----------
    type: str
            Vision deficiency to emulate.

    **Experimental**
    """
    return {"method": "Emulation.setEmulatedVisionDeficiency", "params": {"type": type}}


def set_geolocation_override(
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    accuracy: Optional[float] = None,
) -> dict:
    """Overrides the Geolocation Position or Error. Omitting any of the parameters emulates position
    unavailable.

    Parameters
    ----------
    latitude: Optional[float]
            Mock latitude
    longitude: Optional[float]
            Mock longitude
    accuracy: Optional[float]
            Mock accuracy
    """
    return {
        "method": "Emulation.setGeolocationOverride",
        "params": filter_none(
            {"latitude": latitude, "longitude": longitude, "accuracy": accuracy}
        ),
    }


def set_idle_override(isUserActive: bool, isScreenUnlocked: bool) -> dict:
    """Overrides the Idle state.

    Parameters
    ----------
    isUserActive: bool
            Mock isUserActive
    isScreenUnlocked: bool
            Mock isScreenUnlocked

    **Experimental**
    """
    return {
        "method": "Emulation.setIdleOverride",
        "params": {"isUserActive": isUserActive, "isScreenUnlocked": isScreenUnlocked},
    }


def clear_idle_override() -> dict:
    """Clears Idle state overrides.

    **Experimental**
    """
    return {"method": "Emulation.clearIdleOverride", "params": {}}


@deprecated(version=1.3)
def set_navigator_overrides(platform: str) -> dict:
    """Overrides value returned by the javascript navigator object.

    Parameters
    ----------
    platform: str
            The platform navigator.platform should return.

    **Experimental**
    """
    return {
        "method": "Emulation.setNavigatorOverrides",
        "params": {"platform": platform},
    }


def set_page_scale_factor(pageScaleFactor: float) -> dict:
    """Sets a specified page scale factor.

    Parameters
    ----------
    pageScaleFactor: float
            Page scale factor.

    **Experimental**
    """
    return {
        "method": "Emulation.setPageScaleFactor",
        "params": {"pageScaleFactor": pageScaleFactor},
    }


def set_script_execution_disabled(value: bool) -> dict:
    """Switches script execution in the page.

    Parameters
    ----------
    value: bool
            Whether script execution should be disabled in the page.
    """
    return {
        "method": "Emulation.setScriptExecutionDisabled",
        "params": {"value": value},
    }


def set_touch_emulation_enabled(
    enabled: bool, maxTouchPoints: Optional[int] = None
) -> dict:
    """Enables touch on platforms which do not support them.

    Parameters
    ----------
    enabled: bool
            Whether the touch event emulation should be enabled.
    maxTouchPoints: Optional[int]
            Maximum touch points supported. Defaults to one.
    """
    return {
        "method": "Emulation.setTouchEmulationEnabled",
        "params": filter_none({"enabled": enabled, "maxTouchPoints": maxTouchPoints}),
    }


def set_virtual_time_policy(
    policy: VirtualTimePolicy,
    budget: Optional[float] = None,
    maxVirtualTimeTaskStarvationCount: Optional[int] = None,
    waitForNavigation: Optional[bool] = None,
    initialVirtualTime: Optional[network.TimeSinceEpoch] = None,
) -> Generator[dict, dict, float]:
    """Turns on virtual time for all frames (replacing real-time with a synthetic time source) and sets
    the current virtual time policy.  Note this supersedes any previous time budget.

    Parameters
    ----------
    policy: VirtualTimePolicy
    budget: Optional[float]
            If set, after this many virtual milliseconds have elapsed virtual time will be paused and a
            virtualTimeBudgetExpired event is sent.
    maxVirtualTimeTaskStarvationCount: Optional[int]
            If set this specifies the maximum number of tasks that can be run before virtual is forced
            forwards to prevent deadlock.
    waitForNavigation: Optional[bool]
            If set the virtual time policy change should be deferred until any frame starts navigating.
            Note any previous deferred policy change is superseded.
    initialVirtualTime: Optional[network.TimeSinceEpoch]
            If set, base::Time::Now will be overriden to initially return this value.

    Returns
    -------
    virtualTimeTicksBase: float
            Absolute timestamp at which virtual time was first enabled (up time in milliseconds).

    **Experimental**
    """
    response = yield {
        "method": "Emulation.setVirtualTimePolicy",
        "params": filter_none(
            {
                "policy": policy.value,
                "budget": budget,
                "maxVirtualTimeTaskStarvationCount": maxVirtualTimeTaskStarvationCount,
                "waitForNavigation": waitForNavigation,
                "initialVirtualTime": float(initialVirtualTime)
                if initialVirtualTime
                else None,
            }
        ),
    }
    return response["virtualTimeTicksBase"]


def set_locale_override(locale: Optional[str] = None) -> dict:
    """Overrides default host system locale with the specified one.

    Parameters
    ----------
    locale: Optional[str]
            ICU style C locale (e.g. "en_US"). If not specified or empty, disables the override and
            restores default host system locale.

    **Experimental**
    """
    return {
        "method": "Emulation.setLocaleOverride",
        "params": filter_none({"locale": locale}),
    }


def set_timezone_override(timezoneId: str) -> dict:
    """Overrides default host system timezone with the specified one.

    Parameters
    ----------
    timezoneId: str
            The timezone identifier. If empty, disables the override and
            restores default host system timezone.

    **Experimental**
    """
    return {
        "method": "Emulation.setTimezoneOverride",
        "params": {"timezoneId": timezoneId},
    }


@deprecated(version=1.3)
def set_visible_size(width: int, height: int) -> dict:
    """Resizes the frame/viewport of the page. Note that this does not affect the frame's container
    (e.g. browser window). Can be used to produce screenshots of the specified size. Not supported
    on Android.

    Parameters
    ----------
    width: int
            Frame width (DIP).
    height: int
            Frame height (DIP).

    **Experimental**
    """
    return {
        "method": "Emulation.setVisibleSize",
        "params": {"width": width, "height": height},
    }


def set_disabled_image_types(imageTypes: list[DisabledImageType]) -> dict:
    """
    Parameters
    ----------
    imageTypes: list[DisabledImageType]
            Image types to disable.

    **Experimental**
    """
    return {
        "method": "Emulation.setDisabledImageTypes",
        "params": {"imageTypes": [i.value for i in imageTypes]},
    }


def set_user_agent_override(
    userAgent: str,
    acceptLanguage: Optional[str] = None,
    platform: Optional[str] = None,
    userAgentMetadata: Optional[UserAgentMetadata] = None,
) -> dict:
    """Allows overriding user agent with the given string.

    Parameters
    ----------
    userAgent: str
            User agent to use.
    acceptLanguage: Optional[str]
            Browser langugage to emulate.
    platform: Optional[str]
            The platform navigator.platform should return.
    userAgentMetadata: Optional[UserAgentMetadata]
            To be sent in Sec-CH-UA-* headers and returned in navigator.userAgentData
    """
    return {
        "method": "Emulation.setUserAgentOverride",
        "params": filter_none(
            {
                "userAgent": userAgent,
                "acceptLanguage": acceptLanguage,
                "platform": platform,
                "userAgentMetadata": userAgentMetadata.to_json()
                if userAgentMetadata
                else None,
            }
        ),
    }


@dataclasses.dataclass
class VirtualTimeBudgetExpired:
    """Notification sent after the virtual time budget for the current VirtualTimePolicy has run out."""

    @classmethod
    def from_json(cls, json: dict) -> VirtualTimeBudgetExpired:
        return cls()
