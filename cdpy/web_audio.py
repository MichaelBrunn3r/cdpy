from __future__ import annotations

import dataclasses
import enum
from typing import Optional

from .common import Type, filter_unset_parameters


class GraphObjectId(str):
    """An unique ID for a graph object (AudioContext, AudioNode, AudioParam) in Web Audio API"""

    def __repr__(self):
        return f"GraphObjectId({super().__repr__()})"


class ContextType(enum.Enum):
    """Enum of BaseAudioContext types"""

    REALTIME = "realtime"
    OFFLINE = "offline"


class ContextState(enum.Enum):
    """Enum of AudioContextState from the spec"""

    SUSPENDED = "suspended"
    RUNNING = "running"
    CLOSED = "closed"


class NodeType(str):
    """Enum of AudioNode types"""

    def __repr__(self):
        return f"NodeType({super().__repr__()})"


class ChannelCountMode(enum.Enum):
    """Enum of AudioNode::ChannelCountMode from the spec"""

    CLAMPED_MAX = "clamped-max"
    EXPLICIT = "explicit"
    MAX = "max"


class ChannelInterpretation(enum.Enum):
    """Enum of AudioNode::ChannelInterpretation from the spec"""

    DISCRETE = "discrete"
    SPEAKERS = "speakers"


class ParamType(str):
    """Enum of AudioParam types"""

    def __repr__(self):
        return f"ParamType({super().__repr__()})"


class AutomationRate(enum.Enum):
    """Enum of AudioParam::AutomationRate from the spec"""

    A_RATE = "a-rate"
    K_RATE = "k-rate"


@dataclasses.dataclass
class ContextRealtimeData(Type):
    """Fields in AudioContext that change in real-time.

    Attributes
    ----------
    currentTime: float
            The current context time in second in BaseAudioContext.
    renderCapacity: float
            The time spent on rendering graph divided by render qunatum duration,
            and multiplied by 100. 100 means the audio renderer reached the full
            capacity and glitch may occur.
    callbackIntervalMean: float
            A running mean of callback interval.
    callbackIntervalVariance: float
            A running variance of callback interval.
    """

    currentTime: float
    renderCapacity: float
    callbackIntervalMean: float
    callbackIntervalVariance: float

    @classmethod
    def from_json(cls, json: dict) -> ContextRealtimeData:
        return cls(
            json["currentTime"],
            json["renderCapacity"],
            json["callbackIntervalMean"],
            json["callbackIntervalVariance"],
        )


@dataclasses.dataclass
class BaseAudioContext(Type):
    """Protocol object for BaseAudioContext

    Attributes
    ----------
    contextId: GraphObjectId
    contextType: ContextType
    contextState: ContextState
    callbackBufferSize: float
            Platform-dependent callback buffer size.
    maxOutputChannelCount: float
            Number of output channels supported by audio hardware in use.
    sampleRate: float
            Context sample rate.
    realtimeData: Optional[ContextRealtimeData] = None
    """

    contextId: GraphObjectId
    contextType: ContextType
    contextState: ContextState
    callbackBufferSize: float
    maxOutputChannelCount: float
    sampleRate: float
    realtimeData: Optional[ContextRealtimeData] = None

    @classmethod
    def from_json(cls, json: dict) -> BaseAudioContext:
        return cls(
            GraphObjectId(json["contextId"]),
            ContextType(json["contextType"]),
            ContextState(json["contextState"]),
            json["callbackBufferSize"],
            json["maxOutputChannelCount"],
            json["sampleRate"],
            ContextRealtimeData.from_json(json["realtimeData"])
            if "realtimeData" in json
            else None,
        )


@dataclasses.dataclass
class AudioListener(Type):
    """Protocol object for AudioListener

    Attributes
    ----------
    listenerId: GraphObjectId
    contextId: GraphObjectId
    """

    listenerId: GraphObjectId
    contextId: GraphObjectId

    @classmethod
    def from_json(cls, json: dict) -> AudioListener:
        return cls(GraphObjectId(json["listenerId"]), GraphObjectId(json["contextId"]))


@dataclasses.dataclass
class AudioNode(Type):
    """Protocol object for AudioNode

    Attributes
    ----------
    nodeId: GraphObjectId
    contextId: GraphObjectId
    nodeType: NodeType
    numberOfInputs: float
    numberOfOutputs: float
    channelCount: float
    channelCountMode: ChannelCountMode
    channelInterpretation: ChannelInterpretation
    """

    nodeId: GraphObjectId
    contextId: GraphObjectId
    nodeType: NodeType
    numberOfInputs: float
    numberOfOutputs: float
    channelCount: float
    channelCountMode: ChannelCountMode
    channelInterpretation: ChannelInterpretation

    @classmethod
    def from_json(cls, json: dict) -> AudioNode:
        return cls(
            GraphObjectId(json["nodeId"]),
            GraphObjectId(json["contextId"]),
            NodeType(json["nodeType"]),
            json["numberOfInputs"],
            json["numberOfOutputs"],
            json["channelCount"],
            ChannelCountMode(json["channelCountMode"]),
            ChannelInterpretation(json["channelInterpretation"]),
        )


@dataclasses.dataclass
class AudioParam(Type):
    """Protocol object for AudioParam

    Attributes
    ----------
    paramId: GraphObjectId
    nodeId: GraphObjectId
    contextId: GraphObjectId
    paramType: ParamType
    rate: AutomationRate
    defaultValue: float
    minValue: float
    maxValue: float
    """

    paramId: GraphObjectId
    nodeId: GraphObjectId
    contextId: GraphObjectId
    paramType: ParamType
    rate: AutomationRate
    defaultValue: float
    minValue: float
    maxValue: float

    @classmethod
    def from_json(cls, json: dict) -> AudioParam:
        return cls(
            GraphObjectId(json["paramId"]),
            GraphObjectId(json["nodeId"]),
            GraphObjectId(json["contextId"]),
            ParamType(json["paramType"]),
            AutomationRate(json["rate"]),
            json["defaultValue"],
            json["minValue"],
            json["maxValue"],
        )


def enable():
    """Enables the WebAudio domain and starts sending context lifetime events."""
    return {"method": "WebAudio.enable", "params": {}}


def disable():
    """Disables the WebAudio domain."""
    return {"method": "WebAudio.disable", "params": {}}


def get_realtime_data(contextId: GraphObjectId):
    """Fetch the realtime data from the registered contexts.

    Parameters
    ----------
    contextId: GraphObjectId

    Returns
    -------
    realtimeData: ContextRealtimeData
    """
    return {"method": "WebAudio.getRealtimeData", "params": {"contextId": contextId}}
