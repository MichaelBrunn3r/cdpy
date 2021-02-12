from __future__ import annotations

import dataclasses
import enum
from typing import Generator, Optional

from .common import filter_none


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
class ContextRealtimeData:
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

    def to_json(self) -> dict:
        return {
            "currentTime": self.currentTime,
            "renderCapacity": self.renderCapacity,
            "callbackIntervalMean": self.callbackIntervalMean,
            "callbackIntervalVariance": self.callbackIntervalVariance,
        }


@dataclasses.dataclass
class BaseAudioContext:
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
    realtimeData: Optional[ContextRealtimeData]
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

    def to_json(self) -> dict:
        return filter_none(
            {
                "contextId": str(self.contextId),
                "contextType": self.contextType.value,
                "contextState": self.contextState.value,
                "callbackBufferSize": self.callbackBufferSize,
                "maxOutputChannelCount": self.maxOutputChannelCount,
                "sampleRate": self.sampleRate,
                "realtimeData": self.realtimeData.to_json()
                if self.realtimeData
                else None,
            }
        )


@dataclasses.dataclass
class AudioListener:
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

    def to_json(self) -> dict:
        return {"listenerId": str(self.listenerId), "contextId": str(self.contextId)}


@dataclasses.dataclass
class AudioNode:
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

    def to_json(self) -> dict:
        return {
            "nodeId": str(self.nodeId),
            "contextId": str(self.contextId),
            "nodeType": str(self.nodeType),
            "numberOfInputs": self.numberOfInputs,
            "numberOfOutputs": self.numberOfOutputs,
            "channelCount": self.channelCount,
            "channelCountMode": self.channelCountMode.value,
            "channelInterpretation": self.channelInterpretation.value,
        }


@dataclasses.dataclass
class AudioParam:
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

    def to_json(self) -> dict:
        return {
            "paramId": str(self.paramId),
            "nodeId": str(self.nodeId),
            "contextId": str(self.contextId),
            "paramType": str(self.paramType),
            "rate": self.rate.value,
            "defaultValue": self.defaultValue,
            "minValue": self.minValue,
            "maxValue": self.maxValue,
        }


def enable() -> dict:
    """Enables the WebAudio domain and starts sending context lifetime events."""
    return {"method": "WebAudio.enable", "params": {}}


def disable() -> dict:
    """Disables the WebAudio domain."""
    return {"method": "WebAudio.disable", "params": {}}


def get_realtime_data(
    contextId: GraphObjectId,
) -> Generator[dict, dict, ContextRealtimeData]:
    """Fetch the realtime data from the registered contexts.

    Parameters
    ----------
    contextId: GraphObjectId

    Returns
    -------
    realtimeData: ContextRealtimeData
    """
    response = yield {
        "method": "WebAudio.getRealtimeData",
        "params": {"contextId": str(contextId)},
    }
    return ContextRealtimeData.from_json(response)


@dataclasses.dataclass
class ContextCreated:
    """Notifies that a new BaseAudioContext has been created.

    Attributes
    ----------
    context: BaseAudioContext
    """

    context: BaseAudioContext

    @classmethod
    def from_json(cls, json: dict) -> ContextCreated:
        return cls(BaseAudioContext.from_json(json["context"]))


@dataclasses.dataclass
class ContextWillBeDestroyed:
    """Notifies that an existing BaseAudioContext will be destroyed.

    Attributes
    ----------
    contextId: GraphObjectId
    """

    contextId: GraphObjectId

    @classmethod
    def from_json(cls, json: dict) -> ContextWillBeDestroyed:
        return cls(GraphObjectId(json["contextId"]))


@dataclasses.dataclass
class ContextChanged:
    """Notifies that existing BaseAudioContext has changed some properties (id stays the same)..

    Attributes
    ----------
    context: BaseAudioContext
    """

    context: BaseAudioContext

    @classmethod
    def from_json(cls, json: dict) -> ContextChanged:
        return cls(BaseAudioContext.from_json(json["context"]))


@dataclasses.dataclass
class AudioListenerCreated:
    """Notifies that the construction of an AudioListener has finished.

    Attributes
    ----------
    listener: AudioListener
    """

    listener: AudioListener

    @classmethod
    def from_json(cls, json: dict) -> AudioListenerCreated:
        return cls(AudioListener.from_json(json["listener"]))


@dataclasses.dataclass
class AudioListenerWillBeDestroyed:
    """Notifies that a new AudioListener has been created.

    Attributes
    ----------
    contextId: GraphObjectId
    listenerId: GraphObjectId
    """

    contextId: GraphObjectId
    listenerId: GraphObjectId

    @classmethod
    def from_json(cls, json: dict) -> AudioListenerWillBeDestroyed:
        return cls(GraphObjectId(json["contextId"]), GraphObjectId(json["listenerId"]))


@dataclasses.dataclass
class AudioNodeCreated:
    """Notifies that a new AudioNode has been created.

    Attributes
    ----------
    node: AudioNode
    """

    node: AudioNode

    @classmethod
    def from_json(cls, json: dict) -> AudioNodeCreated:
        return cls(AudioNode.from_json(json["node"]))


@dataclasses.dataclass
class AudioNodeWillBeDestroyed:
    """Notifies that an existing AudioNode has been destroyed.

    Attributes
    ----------
    contextId: GraphObjectId
    nodeId: GraphObjectId
    """

    contextId: GraphObjectId
    nodeId: GraphObjectId

    @classmethod
    def from_json(cls, json: dict) -> AudioNodeWillBeDestroyed:
        return cls(GraphObjectId(json["contextId"]), GraphObjectId(json["nodeId"]))


@dataclasses.dataclass
class AudioParamCreated:
    """Notifies that a new AudioParam has been created.

    Attributes
    ----------
    param: AudioParam
    """

    param: AudioParam

    @classmethod
    def from_json(cls, json: dict) -> AudioParamCreated:
        return cls(AudioParam.from_json(json["param"]))


@dataclasses.dataclass
class AudioParamWillBeDestroyed:
    """Notifies that an existing AudioParam has been destroyed.

    Attributes
    ----------
    contextId: GraphObjectId
    nodeId: GraphObjectId
    paramId: GraphObjectId
    """

    contextId: GraphObjectId
    nodeId: GraphObjectId
    paramId: GraphObjectId

    @classmethod
    def from_json(cls, json: dict) -> AudioParamWillBeDestroyed:
        return cls(
            GraphObjectId(json["contextId"]),
            GraphObjectId(json["nodeId"]),
            GraphObjectId(json["paramId"]),
        )


@dataclasses.dataclass
class NodesConnected:
    """Notifies that two AudioNodes are connected.

    Attributes
    ----------
    contextId: GraphObjectId
    sourceId: GraphObjectId
    destinationId: GraphObjectId
    sourceOutputIndex: Optional[float]
    destinationInputIndex: Optional[float]
    """

    contextId: GraphObjectId
    sourceId: GraphObjectId
    destinationId: GraphObjectId
    sourceOutputIndex: Optional[float] = None
    destinationInputIndex: Optional[float] = None

    @classmethod
    def from_json(cls, json: dict) -> NodesConnected:
        return cls(
            GraphObjectId(json["contextId"]),
            GraphObjectId(json["sourceId"]),
            GraphObjectId(json["destinationId"]),
            json.get("sourceOutputIndex"),
            json.get("destinationInputIndex"),
        )


@dataclasses.dataclass
class NodesDisconnected:
    """Notifies that AudioNodes are disconnected. The destination can be null, and it means all the outgoing connections from the source are disconnected.

    Attributes
    ----------
    contextId: GraphObjectId
    sourceId: GraphObjectId
    destinationId: GraphObjectId
    sourceOutputIndex: Optional[float]
    destinationInputIndex: Optional[float]
    """

    contextId: GraphObjectId
    sourceId: GraphObjectId
    destinationId: GraphObjectId
    sourceOutputIndex: Optional[float] = None
    destinationInputIndex: Optional[float] = None

    @classmethod
    def from_json(cls, json: dict) -> NodesDisconnected:
        return cls(
            GraphObjectId(json["contextId"]),
            GraphObjectId(json["sourceId"]),
            GraphObjectId(json["destinationId"]),
            json.get("sourceOutputIndex"),
            json.get("destinationInputIndex"),
        )


@dataclasses.dataclass
class NodeParamConnected:
    """Notifies that an AudioNode is connected to an AudioParam.

    Attributes
    ----------
    contextId: GraphObjectId
    sourceId: GraphObjectId
    destinationId: GraphObjectId
    sourceOutputIndex: Optional[float]
    """

    contextId: GraphObjectId
    sourceId: GraphObjectId
    destinationId: GraphObjectId
    sourceOutputIndex: Optional[float] = None

    @classmethod
    def from_json(cls, json: dict) -> NodeParamConnected:
        return cls(
            GraphObjectId(json["contextId"]),
            GraphObjectId(json["sourceId"]),
            GraphObjectId(json["destinationId"]),
            json.get("sourceOutputIndex"),
        )


@dataclasses.dataclass
class NodeParamDisconnected:
    """Notifies that an AudioNode is disconnected to an AudioParam.

    Attributes
    ----------
    contextId: GraphObjectId
    sourceId: GraphObjectId
    destinationId: GraphObjectId
    sourceOutputIndex: Optional[float]
    """

    contextId: GraphObjectId
    sourceId: GraphObjectId
    destinationId: GraphObjectId
    sourceOutputIndex: Optional[float] = None

    @classmethod
    def from_json(cls, json: dict) -> NodeParamDisconnected:
        return cls(
            GraphObjectId(json["contextId"]),
            GraphObjectId(json["sourceId"]),
            GraphObjectId(json["destinationId"]),
            json.get("sourceOutputIndex"),
        )
