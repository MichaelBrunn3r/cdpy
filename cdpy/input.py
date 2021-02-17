from __future__ import annotations

import dataclasses
import enum
from typing import Optional

from .common import filter_none


@dataclasses.dataclass
class TouchPoint:
    """
    Attributes
    ----------
    x: float
            X coordinate of the event relative to the main frame's viewport in CSS pixels.
    y: float
            Y coordinate of the event relative to the main frame's viewport in CSS pixels. 0 refers to
            the top of the viewport and Y increases as it proceeds towards the bottom of the viewport.
    radiusX: Optional[float]
            X radius of the touch area (default: 1.0).
    radiusY: Optional[float]
            Y radius of the touch area (default: 1.0).
    rotationAngle: Optional[float]
            Rotation angle (default: 0.0).
    force: Optional[float]
            Force (default: 1.0).
    tangentialPressure: Optional[float]
            The normalized tangential pressure, which has a range of [-1,1] (default: 0).
    tiltX: Optional[int]
            The plane angle between the Y-Z plane and the plane containing both the stylus axis and the Y axis, in degrees of the range [-90,90], a positive tiltX is to the right (default: 0)
    tiltY: Optional[int]
            The plane angle between the X-Z plane and the plane containing both the stylus axis and the X axis, in degrees of the range [-90,90], a positive tiltY is towards the user (default: 0).
    twist: Optional[int]
            The clockwise rotation of a pen stylus around its own major axis, in degrees in the range [0,359] (default: 0).
    id: Optional[float]
            Identifier used to track touch sources between events, must be unique within an event.
    """

    x: float
    y: float
    radiusX: Optional[float] = None
    radiusY: Optional[float] = None
    rotationAngle: Optional[float] = None
    force: Optional[float] = None
    tangentialPressure: Optional[float] = None
    tiltX: Optional[int] = None
    tiltY: Optional[int] = None
    twist: Optional[int] = None
    id: Optional[float] = None

    @classmethod
    def from_json(cls, json: dict) -> TouchPoint:
        return cls(
            json["x"],
            json["y"],
            json.get("radiusX"),
            json.get("radiusY"),
            json.get("rotationAngle"),
            json.get("force"),
            json.get("tangentialPressure"),
            json.get("tiltX"),
            json.get("tiltY"),
            json.get("twist"),
            json.get("id"),
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "x": self.x,
                "y": self.y,
                "radiusX": self.radiusX,
                "radiusY": self.radiusY,
                "rotationAngle": self.rotationAngle,
                "force": self.force,
                "tangentialPressure": self.tangentialPressure,
                "tiltX": self.tiltX,
                "tiltY": self.tiltY,
                "twist": self.twist,
                "id": self.id,
            }
        )


class GestureSourceType(enum.Enum):
    """"""

    DEFAULT = "default"
    TOUCH = "touch"
    MOUSE = "mouse"


class MouseButton(enum.Enum):
    """"""

    NONE = "none"
    LEFT = "left"
    MIDDLE = "middle"
    RIGHT = "right"
    BACK = "back"
    FORWARD = "forward"


class TimeSinceEpoch(float):
    """UTC time in seconds, counted from January 1, 1970."""

    def __repr__(self):
        return f"TimeSinceEpoch({super().__repr__()})"


def dispatch_key_event(
    type: str,
    modifiers: Optional[int] = None,
    timestamp: Optional[TimeSinceEpoch] = None,
    text: Optional[str] = None,
    unmodifiedText: Optional[str] = None,
    keyIdentifier: Optional[str] = None,
    code: Optional[str] = None,
    key: Optional[str] = None,
    windowsVirtualKeyCode: Optional[int] = None,
    nativeVirtualKeyCode: Optional[int] = None,
    autoRepeat: Optional[bool] = None,
    isKeypad: Optional[bool] = None,
    isSystemKey: Optional[bool] = None,
    location: Optional[int] = None,
    commands: Optional[list[str]] = None,
) -> dict:
    """Dispatches a key event to the page.

    Parameters
    ----------
    type: str
            Type of the key event.
    modifiers: Optional[int]
            Bit field representing pressed modifier keys. Alt=1, Ctrl=2, Meta/Command=4, Shift=8
            (default: 0).
    timestamp: Optional[TimeSinceEpoch]
            Time at which the event occurred.
    text: Optional[str]
            Text as generated by processing a virtual key code with a keyboard layout. Not needed for
            for `keyUp` and `rawKeyDown` events (default: "")
    unmodifiedText: Optional[str]
            Text that would have been generated by the keyboard if no modifiers were pressed (except for
            shift). Useful for shortcut (accelerator) key handling (default: "").
    keyIdentifier: Optional[str]
            Unique key identifier (e.g., 'U+0041') (default: "").
    code: Optional[str]
            Unique DOM defined string value for each physical key (e.g., 'KeyA') (default: "").
    key: Optional[str]
            Unique DOM defined string value describing the meaning of the key in the context of active
            modifiers, keyboard layout, etc (e.g., 'AltGr') (default: "").
    windowsVirtualKeyCode: Optional[int]
            Windows virtual key code (default: 0).
    nativeVirtualKeyCode: Optional[int]
            Native virtual key code (default: 0).
    autoRepeat: Optional[bool]
            Whether the event was generated from auto repeat (default: false).
    isKeypad: Optional[bool]
            Whether the event was generated from the keypad (default: false).
    isSystemKey: Optional[bool]
            Whether the event was a system key event (default: false).
    location: Optional[int]
            Whether the event was from the left or right side of the keyboard. 1=Left, 2=Right (default:
            0).
    commands: Optional[list[str]]
            Editing commands to send with the key event (e.g., 'selectAll') (default: []).
            These are related to but not equal the command names used in `document.execCommand` and NSStandardKeyBindingResponding.
            See https://source.chromium.org/chromium/chromium/src/+/master:third_party/blink/renderer/core/editing/commands/editor_command_names.h for valid command names.
    """
    return {
        "method": "Input.dispatchKeyEvent",
        "params": filter_none(
            {
                "type": type,
                "modifiers": modifiers,
                "timestamp": float(timestamp) if timestamp else None,
                "text": text,
                "unmodifiedText": unmodifiedText,
                "keyIdentifier": keyIdentifier,
                "code": code,
                "key": key,
                "windowsVirtualKeyCode": windowsVirtualKeyCode,
                "nativeVirtualKeyCode": nativeVirtualKeyCode,
                "autoRepeat": autoRepeat,
                "isKeypad": isKeypad,
                "isSystemKey": isSystemKey,
                "location": location,
                "commands": commands,
            }
        ),
    }


def insert_text(text: str) -> dict:
    """This method emulates inserting text that doesn't come from a key press,
    for example an emoji keyboard or an IME.

    Parameters
    ----------
    text: str
            The text to insert.

    **Experimental**
    """
    return {"method": "Input.insertText", "params": {"text": text}}


def dispatch_mouse_event(
    type: str,
    x: float,
    y: float,
    modifiers: Optional[int] = None,
    timestamp: Optional[TimeSinceEpoch] = None,
    button: Optional[MouseButton] = None,
    buttons: Optional[int] = None,
    clickCount: Optional[int] = None,
    force: Optional[float] = None,
    tangentialPressure: Optional[float] = None,
    tiltX: Optional[int] = None,
    tiltY: Optional[int] = None,
    twist: Optional[int] = None,
    deltaX: Optional[float] = None,
    deltaY: Optional[float] = None,
    pointerType: Optional[str] = None,
) -> dict:
    """Dispatches a mouse event to the page.

    Parameters
    ----------
    type: str
            Type of the mouse event.
    x: float
            X coordinate of the event relative to the main frame's viewport in CSS pixels.
    y: float
            Y coordinate of the event relative to the main frame's viewport in CSS pixels. 0 refers to
            the top of the viewport and Y increases as it proceeds towards the bottom of the viewport.
    modifiers: Optional[int]
            Bit field representing pressed modifier keys. Alt=1, Ctrl=2, Meta/Command=4, Shift=8
            (default: 0).
    timestamp: Optional[TimeSinceEpoch]
            Time at which the event occurred.
    button: Optional[MouseButton]
            Mouse button (default: "none").
    buttons: Optional[int]
            A number indicating which buttons are pressed on the mouse when a mouse event is triggered.
            Left=1, Right=2, Middle=4, Back=8, Forward=16, None=0.
    clickCount: Optional[int]
            Number of times the mouse button was clicked (default: 0).
    force: Optional[float]
            The normalized pressure, which has a range of [0,1] (default: 0).
    tangentialPressure: Optional[float]
            The normalized tangential pressure, which has a range of [-1,1] (default: 0).
    tiltX: Optional[int]
            The plane angle between the Y-Z plane and the plane containing both the stylus axis and the Y axis, in degrees of the range [-90,90], a positive tiltX is to the right (default: 0).
    tiltY: Optional[int]
            The plane angle between the X-Z plane and the plane containing both the stylus axis and the X axis, in degrees of the range [-90,90], a positive tiltY is towards the user (default: 0).
    twist: Optional[int]
            The clockwise rotation of a pen stylus around its own major axis, in degrees in the range [0,359] (default: 0).
    deltaX: Optional[float]
            X delta in CSS pixels for mouse wheel event (default: 0).
    deltaY: Optional[float]
            Y delta in CSS pixels for mouse wheel event (default: 0).
    pointerType: Optional[str]
            Pointer type (default: "mouse").
    """
    return {
        "method": "Input.dispatchMouseEvent",
        "params": filter_none(
            {
                "type": type,
                "x": x,
                "y": y,
                "modifiers": modifiers,
                "timestamp": float(timestamp) if timestamp else None,
                "button": button.value if button else None,
                "buttons": buttons,
                "clickCount": clickCount,
                "force": force,
                "tangentialPressure": tangentialPressure,
                "tiltX": tiltX,
                "tiltY": tiltY,
                "twist": twist,
                "deltaX": deltaX,
                "deltaY": deltaY,
                "pointerType": pointerType,
            }
        ),
    }


def dispatch_touch_event(
    type: str,
    touchPoints: list[TouchPoint],
    modifiers: Optional[int] = None,
    timestamp: Optional[TimeSinceEpoch] = None,
) -> dict:
    """Dispatches a touch event to the page.

    Parameters
    ----------
    type: str
            Type of the touch event. TouchEnd and TouchCancel must not contain any touch points, while
            TouchStart and TouchMove must contains at least one.
    touchPoints: list[TouchPoint]
            Active touch points on the touch device. One event per any changed point (compared to
            previous touch event in a sequence) is generated, emulating pressing/moving/releasing points
            one by one.
    modifiers: Optional[int]
            Bit field representing pressed modifier keys. Alt=1, Ctrl=2, Meta/Command=4, Shift=8
            (default: 0).
    timestamp: Optional[TimeSinceEpoch]
            Time at which the event occurred.
    """
    return {
        "method": "Input.dispatchTouchEvent",
        "params": filter_none(
            {
                "type": type,
                "touchPoints": [t.to_json() for t in touchPoints],
                "modifiers": modifiers,
                "timestamp": float(timestamp) if timestamp else None,
            }
        ),
    }


def emulate_touch_from_mouse_event(
    type: str,
    x: int,
    y: int,
    button: MouseButton,
    timestamp: Optional[TimeSinceEpoch] = None,
    deltaX: Optional[float] = None,
    deltaY: Optional[float] = None,
    modifiers: Optional[int] = None,
    clickCount: Optional[int] = None,
) -> dict:
    """Emulates touch event from the mouse event parameters.

    Parameters
    ----------
    type: str
            Type of the mouse event.
    x: int
            X coordinate of the mouse pointer in DIP.
    y: int
            Y coordinate of the mouse pointer in DIP.
    button: MouseButton
            Mouse button. Only "none", "left", "right" are supported.
    timestamp: Optional[TimeSinceEpoch]
            Time at which the event occurred (default: current time).
    deltaX: Optional[float]
            X delta in DIP for mouse wheel event (default: 0).
    deltaY: Optional[float]
            Y delta in DIP for mouse wheel event (default: 0).
    modifiers: Optional[int]
            Bit field representing pressed modifier keys. Alt=1, Ctrl=2, Meta/Command=4, Shift=8
            (default: 0).
    clickCount: Optional[int]
            Number of times the mouse button was clicked (default: 0).

    **Experimental**
    """
    return {
        "method": "Input.emulateTouchFromMouseEvent",
        "params": filter_none(
            {
                "type": type,
                "x": x,
                "y": y,
                "button": button.value,
                "timestamp": float(timestamp) if timestamp else None,
                "deltaX": deltaX,
                "deltaY": deltaY,
                "modifiers": modifiers,
                "clickCount": clickCount,
            }
        ),
    }


def set_ignore_input_events(ignore: bool) -> dict:
    """Ignores input events (useful while auditing page).

    Parameters
    ----------
    ignore: bool
            Ignores input events processing when set to true.
    """
    return {"method": "Input.setIgnoreInputEvents", "params": {"ignore": ignore}}


def synthesize_pinch_gesture(
    x: float,
    y: float,
    scaleFactor: float,
    relativeSpeed: Optional[int] = None,
    gestureSourceType: Optional[GestureSourceType] = None,
) -> dict:
    """Synthesizes a pinch gesture over a time period by issuing appropriate touch events.

    Parameters
    ----------
    x: float
            X coordinate of the start of the gesture in CSS pixels.
    y: float
            Y coordinate of the start of the gesture in CSS pixels.
    scaleFactor: float
            Relative scale factor after zooming (>1.0 zooms in, <1.0 zooms out).
    relativeSpeed: Optional[int]
            Relative pointer speed in pixels per second (default: 800).
    gestureSourceType: Optional[GestureSourceType]
            Which type of input events to be generated (default: 'default', which queries the platform
            for the preferred input type).

    **Experimental**
    """
    return {
        "method": "Input.synthesizePinchGesture",
        "params": filter_none(
            {
                "x": x,
                "y": y,
                "scaleFactor": scaleFactor,
                "relativeSpeed": relativeSpeed,
                "gestureSourceType": gestureSourceType.value
                if gestureSourceType
                else None,
            }
        ),
    }


def synthesize_scroll_gesture(
    x: float,
    y: float,
    xDistance: Optional[float] = None,
    yDistance: Optional[float] = None,
    xOverscroll: Optional[float] = None,
    yOverscroll: Optional[float] = None,
    preventFling: Optional[bool] = None,
    speed: Optional[int] = None,
    gestureSourceType: Optional[GestureSourceType] = None,
    repeatCount: Optional[int] = None,
    repeatDelayMs: Optional[int] = None,
    interactionMarkerName: Optional[str] = None,
) -> dict:
    """Synthesizes a scroll gesture over a time period by issuing appropriate touch events.

    Parameters
    ----------
    x: float
            X coordinate of the start of the gesture in CSS pixels.
    y: float
            Y coordinate of the start of the gesture in CSS pixels.
    xDistance: Optional[float]
            The distance to scroll along the X axis (positive to scroll left).
    yDistance: Optional[float]
            The distance to scroll along the Y axis (positive to scroll up).
    xOverscroll: Optional[float]
            The number of additional pixels to scroll back along the X axis, in addition to the given
            distance.
    yOverscroll: Optional[float]
            The number of additional pixels to scroll back along the Y axis, in addition to the given
            distance.
    preventFling: Optional[bool]
            Prevent fling (default: true).
    speed: Optional[int]
            Swipe speed in pixels per second (default: 800).
    gestureSourceType: Optional[GestureSourceType]
            Which type of input events to be generated (default: 'default', which queries the platform
            for the preferred input type).
    repeatCount: Optional[int]
            The number of times to repeat the gesture (default: 0).
    repeatDelayMs: Optional[int]
            The number of milliseconds delay between each repeat. (default: 250).
    interactionMarkerName: Optional[str]
            The name of the interaction markers to generate, if not empty (default: "").

    **Experimental**
    """
    return {
        "method": "Input.synthesizeScrollGesture",
        "params": filter_none(
            {
                "x": x,
                "y": y,
                "xDistance": xDistance,
                "yDistance": yDistance,
                "xOverscroll": xOverscroll,
                "yOverscroll": yOverscroll,
                "preventFling": preventFling,
                "speed": speed,
                "gestureSourceType": gestureSourceType.value
                if gestureSourceType
                else None,
                "repeatCount": repeatCount,
                "repeatDelayMs": repeatDelayMs,
                "interactionMarkerName": interactionMarkerName,
            }
        ),
    }


def synthesize_tap_gesture(
    x: float,
    y: float,
    duration: Optional[int] = None,
    tapCount: Optional[int] = None,
    gestureSourceType: Optional[GestureSourceType] = None,
) -> dict:
    """Synthesizes a tap gesture over a time period by issuing appropriate touch events.

    Parameters
    ----------
    x: float
            X coordinate of the start of the gesture in CSS pixels.
    y: float
            Y coordinate of the start of the gesture in CSS pixels.
    duration: Optional[int]
            Duration between touchdown and touchup events in ms (default: 50).
    tapCount: Optional[int]
            Number of times to perform the tap (e.g. 2 for double tap, default: 1).
    gestureSourceType: Optional[GestureSourceType]
            Which type of input events to be generated (default: 'default', which queries the platform
            for the preferred input type).

    **Experimental**
    """
    return {
        "method": "Input.synthesizeTapGesture",
        "params": filter_none(
            {
                "x": x,
                "y": y,
                "duration": duration,
                "tapCount": tapCount,
                "gestureSourceType": gestureSourceType.value
                if gestureSourceType
                else None,
            }
        ),
    }
