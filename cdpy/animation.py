from __future__ import annotations

import dataclasses
from typing import Optional

from . import dom, runtime
from .common import filter_none


@dataclasses.dataclass
class Animation:
    """Animation instance.

    Attributes
    ----------
    id: str
            `Animation`'s id.
    name: str
            `Animation`'s name.
    pausedState: bool
            `Animation`'s internal paused state.
    playState: str
            `Animation`'s play state.
    playbackRate: float
            `Animation`'s playback rate.
    startTime: float
            `Animation`'s start time.
    currentTime: float
            `Animation`'s current time.
    type: str
            Animation type of `Animation`.
    source: Optional[AnimationEffect]
            `Animation`'s source animation node.
    cssId: Optional[str]
            A unique ID for `Animation` representing the sources that triggered this CSS
            animation/transition.
    """

    id: str
    name: str
    pausedState: bool
    playState: str
    playbackRate: float
    startTime: float
    currentTime: float
    type: str
    source: Optional[AnimationEffect] = None
    cssId: Optional[str] = None

    @classmethod
    def from_json(cls, json: dict) -> Animation:
        return cls(
            json["id"],
            json["name"],
            json["pausedState"],
            json["playState"],
            json["playbackRate"],
            json["startTime"],
            json["currentTime"],
            json["type"],
            AnimationEffect.from_json(json["source"]) if "source" in json else None,
            json.get("cssId"),
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "id": self.id,
                "name": self.name,
                "pausedState": self.pausedState,
                "playState": self.playState,
                "playbackRate": self.playbackRate,
                "startTime": self.startTime,
                "currentTime": self.currentTime,
                "type": self.type,
                "source": self.source.to_json() if self.source else None,
                "cssId": self.cssId,
            }
        )


@dataclasses.dataclass
class AnimationEffect:
    """AnimationEffect instance

    Attributes
    ----------
    delay: float
            `AnimationEffect`'s delay.
    endDelay: float
            `AnimationEffect`'s end delay.
    iterationStart: float
            `AnimationEffect`'s iteration start.
    iterations: float
            `AnimationEffect`'s iterations.
    duration: float
            `AnimationEffect`'s iteration duration.
    direction: str
            `AnimationEffect`'s playback direction.
    fill: str
            `AnimationEffect`'s fill mode.
    easing: str
            `AnimationEffect`'s timing function.
    backendNodeId: Optional[dom.BackendNodeId]
            `AnimationEffect`'s target node.
    keyframesRule: Optional[KeyframesRule]
            `AnimationEffect`'s keyframes.
    """

    delay: float
    endDelay: float
    iterationStart: float
    iterations: float
    duration: float
    direction: str
    fill: str
    easing: str
    backendNodeId: Optional[dom.BackendNodeId] = None
    keyframesRule: Optional[KeyframesRule] = None

    @classmethod
    def from_json(cls, json: dict) -> AnimationEffect:
        return cls(
            json["delay"],
            json["endDelay"],
            json["iterationStart"],
            json["iterations"],
            json["duration"],
            json["direction"],
            json["fill"],
            json["easing"],
            dom.BackendNodeId(json["backendNodeId"])
            if "backendNodeId" in json
            else None,
            KeyframesRule.from_json(json["keyframesRule"])
            if "keyframesRule" in json
            else None,
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "delay": self.delay,
                "endDelay": self.endDelay,
                "iterationStart": self.iterationStart,
                "iterations": self.iterations,
                "duration": self.duration,
                "direction": self.direction,
                "fill": self.fill,
                "easing": self.easing,
                "backendNodeId": int(self.backendNodeId)
                if self.backendNodeId
                else None,
                "keyframesRule": self.keyframesRule.to_json()
                if self.keyframesRule
                else None,
            }
        )


@dataclasses.dataclass
class KeyframesRule:
    """Keyframes Rule

    Attributes
    ----------
    keyframes: list[KeyframeStyle]
            List of animation keyframes.
    name: Optional[str]
            CSS keyframed animation's name.
    """

    keyframes: list[KeyframeStyle]
    name: Optional[str] = None

    @classmethod
    def from_json(cls, json: dict) -> KeyframesRule:
        return cls(
            [KeyframeStyle.from_json(x) for x in json["keyframes"]], json.get("name")
        )

    def to_json(self) -> dict:
        return filter_none(
            {"keyframes": [k.to_json() for k in self.keyframes], "name": self.name}
        )


@dataclasses.dataclass
class KeyframeStyle:
    """Keyframe Style

    Attributes
    ----------
    offset: str
            Keyframe's time offset.
    easing: str
            `AnimationEffect`'s timing function.
    """

    offset: str
    easing: str

    @classmethod
    def from_json(cls, json: dict) -> KeyframeStyle:
        return cls(json["offset"], json["easing"])

    def to_json(self) -> dict:
        return {"offset": self.offset, "easing": self.easing}


def disable():
    """Disables animation domain notifications."""
    return {"method": "Animation.disable", "params": {}}


def enable():
    """Enables animation domain notifications."""
    return {"method": "Animation.enable", "params": {}}


def get_current_time(id: str):
    """Returns the current time of the an animation.

    Parameters
    ----------
    id: str
            Id of animation.

    Returns
    -------
    currentTime: float
            Current time of the page.
    """
    return {"method": "Animation.getCurrentTime", "params": {"id": id}}


def get_playback_rate():
    """Gets the playback rate of the document timeline.

    Returns
    -------
    playbackRate: float
            Playback rate for animations on page.
    """
    return {"method": "Animation.getPlaybackRate", "params": {}}


def release_animations(animations: list[str]):
    """Releases a set of animations to no longer be manipulated.

    Parameters
    ----------
    animations: list[str]
            List of animation ids to seek.
    """
    return {
        "method": "Animation.releaseAnimations",
        "params": {"animations": animations},
    }


def resolve_animation(animationId: str):
    """Gets the remote object of the Animation.

    Parameters
    ----------
    animationId: str
            Animation id.

    Returns
    -------
    remoteObject: runtime.RemoteObject
            Corresponding remote object.
    """
    return {
        "method": "Animation.resolveAnimation",
        "params": {"animationId": animationId},
    }


def seek_animations(animations: list[str], currentTime: float):
    """Seek a set of animations to a particular time within each animation.

    Parameters
    ----------
    animations: list[str]
            List of animation ids to seek.
    currentTime: float
            Set the current time of each animation.
    """
    return {
        "method": "Animation.seekAnimations",
        "params": {"animations": animations, "currentTime": currentTime},
    }


def set_paused(animations: list[str], paused: bool):
    """Sets the paused state of a set of animations.

    Parameters
    ----------
    animations: list[str]
            Animations to set the pause state of.
    paused: bool
            Paused state to set to.
    """
    return {
        "method": "Animation.setPaused",
        "params": {"animations": animations, "paused": paused},
    }


def set_playback_rate(playbackRate: float):
    """Sets the playback rate of the document timeline.

    Parameters
    ----------
    playbackRate: float
            Playback rate for animations on page
    """
    return {
        "method": "Animation.setPlaybackRate",
        "params": {"playbackRate": playbackRate},
    }


def set_timing(animationId: str, duration: float, delay: float):
    """Sets the timing of an animation node.

    Parameters
    ----------
    animationId: str
            Animation id.
    duration: float
            Duration of the animation.
    delay: float
            Delay of the animation.
    """
    return {
        "method": "Animation.setTiming",
        "params": {"animationId": animationId, "duration": duration, "delay": delay},
    }
