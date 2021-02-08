from __future__ import annotations

import dataclasses
import enum
from typing import Optional

from .common import Type, filter_unset_parameters


@dataclasses.dataclass
class ScreenshotParams(Type):
    """Encoding options for a screenshot.

    Attributes
    ----------
    format: Optional[str] = None
            Image compression format (defaults to png).
    quality: Optional[int] = None
            Compression quality from range [0..100] (jpeg only).
    """

    format: Optional[str] = None
    quality: Optional[int] = None

    @classmethod
    def from_json(cls, json: dict) -> ScreenshotParams:
        return cls(json.get("quality"))


def begin_frame(
    frameTimeTicks: Optional[float] = None,
    interval: Optional[float] = None,
    noDisplayUpdates: Optional[bool] = None,
    screenshot: Optional[ScreenshotParams] = None,
):
    """Sends a BeginFrame to the target and returns when the frame was completed. Optionally captures a
    screenshot from the resulting frame. Requires that the target was created with enabled
    BeginFrameControl. Designed for use with --run-all-compositor-stages-before-draw, see also
    https://goo.gl/3zHXhB for more background.

    Parameters
    ----------
    frameTimeTicks: Optional[float]
            Timestamp of this BeginFrame in Renderer TimeTicks (milliseconds of uptime). If not set,
            the current time will be used.
    interval: Optional[float]
            The interval between BeginFrames that is reported to the compositor, in milliseconds.
            Defaults to a 60 frames/second interval, i.e. about 16.666 milliseconds.
    noDisplayUpdates: Optional[bool]
            Whether updates should not be committed and drawn onto the display. False by default. If
            true, only side effects of the BeginFrame will be run, such as layout and animations, but
            any visual updates may not be visible on the display or in screenshots.
    screenshot: Optional[ScreenshotParams]
            If set, a screenshot of the frame will be captured and returned in the response. Otherwise,
            no screenshot will be captured. Note that capturing a screenshot can fail, for example,
            during renderer initialization. In such a case, no screenshot data will be returned.

    Returns
    -------
    hasDamage: bool
            Whether the BeginFrame resulted in damage and, thus, a new frame was committed to the
            display. Reported for diagnostic uses, may be removed in the future.
    screenshotData: Optional[str]
            Base64-encoded image data of the screenshot, if one was requested and successfully taken. (Encoded as a base64 string when passed over JSON)
    """
    return filter_unset_parameters(
        {
            "method": "HeadlessExperimental.beginFrame",
            "params": {
                "frameTimeTicks": frameTimeTicks,
                "interval": interval,
                "noDisplayUpdates": noDisplayUpdates,
                "screenshot": screenshot,
            },
        }
    )


def disable():
    """Disables headless events for the target."""
    return {"method": "HeadlessExperimental.disable", "params": {}}


def enable():
    """Enables headless events for the target."""
    return {"method": "HeadlessExperimental.enable", "params": {}}
