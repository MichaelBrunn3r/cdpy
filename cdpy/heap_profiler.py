from __future__ import annotations

import dataclasses
from typing import Generator, Optional

from . import runtime
from .common import filter_unset_parameters


class HeapSnapshotObjectId(str):
    """Heap snapshot object id."""

    def __repr__(self):
        return f"HeapSnapshotObjectId({super().__repr__()})"


@dataclasses.dataclass
class SamplingHeapProfileNode:
    """Sampling Heap Profile node. Holds callsite information, allocation statistics and child nodes.

    Attributes
    ----------
    callFrame: runtime.CallFrame
            Function location.
    selfSize: float
            Allocations size in bytes for the node excluding children.
    id: int
            Node id. Ids are unique across all profiles collected between startSampling and stopSampling.
    children: list[SamplingHeapProfileNode]
            Child nodes.
    """

    callFrame: runtime.CallFrame
    selfSize: float
    id: int
    children: list[SamplingHeapProfileNode]

    @classmethod
    def from_json(cls, json: dict) -> SamplingHeapProfileNode:
        return cls(
            runtime.CallFrame.from_json(json["callFrame"]),
            json["selfSize"],
            json["id"],
            [SamplingHeapProfileNode.from_json(c) for c in json["children"]],
        )

    def to_json(self) -> dict:
        return {
            "callFrame": self.callFrame.to_json(),
            "selfSize": self.selfSize,
            "id": self.id,
            "children": [c.to_json() for c in self.children],
        }


@dataclasses.dataclass
class SamplingHeapProfileSample:
    """A single sample from a sampling profile.

    Attributes
    ----------
    size: float
            Allocation size in bytes attributed to the sample.
    nodeId: int
            Id of the corresponding profile tree node.
    ordinal: float
            Time-ordered sample ordinal number. It is unique across all profiles retrieved
            between startSampling and stopSampling.
    """

    size: float
    nodeId: int
    ordinal: float

    @classmethod
    def from_json(cls, json: dict) -> SamplingHeapProfileSample:
        return cls(json["size"], json["nodeId"], json["ordinal"])

    def to_json(self) -> dict:
        return {"size": self.size, "nodeId": self.nodeId, "ordinal": self.ordinal}


@dataclasses.dataclass
class SamplingHeapProfile:
    """Sampling profile.

    Attributes
    ----------
    head: SamplingHeapProfileNode
    samples: list[SamplingHeapProfileSample]
    """

    head: SamplingHeapProfileNode
    samples: list[SamplingHeapProfileSample]

    @classmethod
    def from_json(cls, json: dict) -> SamplingHeapProfile:
        return cls(
            SamplingHeapProfileNode.from_json(json["head"]),
            [SamplingHeapProfileSample.from_json(s) for s in json["samples"]],
        )

    def to_json(self) -> dict:
        return {
            "head": self.head.to_json(),
            "samples": [s.to_json() for s in self.samples],
        }


def add_inspected_heap_object(heapObjectId: HeapSnapshotObjectId) -> dict:
    """Enables console to refer to the node with given id via $x (see Command Line API for more details
    $x functions).

    Parameters
    ----------
    heapObjectId: HeapSnapshotObjectId
            Heap snapshot object id to be accessible by means of $x command line API.
    """
    return {
        "method": "HeapProfiler.addInspectedHeapObject",
        "params": {"heapObjectId": str(heapObjectId)},
    }


def collect_garbage() -> dict:
    """"""
    return {"method": "HeapProfiler.collectGarbage", "params": {}}


def disable() -> dict:
    """"""
    return {"method": "HeapProfiler.disable", "params": {}}


def enable() -> dict:
    """"""
    return {"method": "HeapProfiler.enable", "params": {}}


def get_heap_object_id(
    objectId: runtime.RemoteObjectId,
) -> Generator[dict, dict, HeapSnapshotObjectId]:
    """
    Parameters
    ----------
    objectId: runtime.RemoteObjectId
            Identifier of the object to get heap object id for.

    Returns
    -------
    heapSnapshotObjectId: HeapSnapshotObjectId
            Id of the heap snapshot object corresponding to the passed remote object id.
    """
    response = yield {
        "method": "HeapProfiler.getHeapObjectId",
        "params": {"objectId": str(objectId)},
    }
    return HeapSnapshotObjectId(response)


def get_object_by_heap_object_id(
    objectId: HeapSnapshotObjectId, objectGroup: Optional[str] = None
) -> Generator[dict, dict, runtime.RemoteObject]:
    """
    Parameters
    ----------
    objectId: HeapSnapshotObjectId
    objectGroup: Optional[str]
            Symbolic group name that can be used to release multiple objects.

    Returns
    -------
    result: runtime.RemoteObject
            Evaluation result.
    """
    response = yield filter_unset_parameters(
        {
            "method": "HeapProfiler.getObjectByHeapObjectId",
            "params": {"objectId": str(objectId), "objectGroup": objectGroup},
        }
    )
    return runtime.RemoteObject.from_json(response)


def get_sampling_profile() -> Generator[dict, dict, SamplingHeapProfile]:
    """
    Returns
    -------
    profile: SamplingHeapProfile
            Return the sampling profile being collected.
    """
    response = yield {"method": "HeapProfiler.getSamplingProfile", "params": {}}
    return SamplingHeapProfile.from_json(response)


def start_sampling(samplingInterval: Optional[float] = None) -> dict:
    """
    Parameters
    ----------
    samplingInterval: Optional[float]
            Average sample interval in bytes. Poisson distribution is used for the intervals. The
            default value is 32768 bytes.
    """
    return filter_unset_parameters(
        {
            "method": "HeapProfiler.startSampling",
            "params": {"samplingInterval": samplingInterval},
        }
    )


def start_tracking_heap_objects(trackAllocations: Optional[bool] = None) -> dict:
    """
    Parameters
    ----------
    trackAllocations: Optional[bool]
    """
    return filter_unset_parameters(
        {
            "method": "HeapProfiler.startTrackingHeapObjects",
            "params": {"trackAllocations": trackAllocations},
        }
    )


def stop_sampling() -> Generator[dict, dict, SamplingHeapProfile]:
    """
    Returns
    -------
    profile: SamplingHeapProfile
            Recorded sampling heap profile.
    """
    response = yield {"method": "HeapProfiler.stopSampling", "params": {}}
    return SamplingHeapProfile.from_json(response)


def stop_tracking_heap_objects(
    reportProgress: Optional[bool] = None,
    treatGlobalObjectsAsRoots: Optional[bool] = None,
) -> dict:
    """
    Parameters
    ----------
    reportProgress: Optional[bool]
            If true 'reportHeapSnapshotProgress' events will be generated while snapshot is being taken
            when the tracking is stopped.
    treatGlobalObjectsAsRoots: Optional[bool]
    """
    return filter_unset_parameters(
        {
            "method": "HeapProfiler.stopTrackingHeapObjects",
            "params": {
                "reportProgress": reportProgress,
                "treatGlobalObjectsAsRoots": treatGlobalObjectsAsRoots,
            },
        }
    )


def take_heap_snapshot(
    reportProgress: Optional[bool] = None,
    treatGlobalObjectsAsRoots: Optional[bool] = None,
) -> dict:
    """
    Parameters
    ----------
    reportProgress: Optional[bool]
            If true 'reportHeapSnapshotProgress' events will be generated while snapshot is being taken.
    treatGlobalObjectsAsRoots: Optional[bool]
            If true, a raw snapshot without artifical roots will be generated
    """
    return filter_unset_parameters(
        {
            "method": "HeapProfiler.takeHeapSnapshot",
            "params": {
                "reportProgress": reportProgress,
                "treatGlobalObjectsAsRoots": treatGlobalObjectsAsRoots,
            },
        }
    )


@dataclasses.dataclass
class AddHeapSnapshotChunk:
    """
    Attributes
    ----------
    chunk: str
    """

    chunk: str

    @classmethod
    def from_json(cls, json: dict) -> AddHeapSnapshotChunk:
        return cls(json["chunk"])


@dataclasses.dataclass
class HeapStatsUpdate:
    """If heap objects tracking has been started then backend may send update for one or more fragments

    Attributes
    ----------
    statsUpdate: list[int]
            An array of triplets. Each triplet describes a fragment. The first integer is the fragment
            index, the second integer is a total count of objects for the fragment, the third integer is
            a total size of the objects for the fragment.
    """

    statsUpdate: list[int]

    @classmethod
    def from_json(cls, json: dict) -> HeapStatsUpdate:
        return cls(json["statsUpdate"])


@dataclasses.dataclass
class LastSeenObjectId:
    """If heap objects tracking has been started then backend regularly sends a current value for last
    seen object id and corresponding timestamp. If the were changes in the heap since last event
    then one or more heapStatsUpdate events will be sent before a new lastSeenObjectId event.

    Attributes
    ----------
    lastSeenObjectId: int
    timestamp: float
    """

    lastSeenObjectId: int
    timestamp: float

    @classmethod
    def from_json(cls, json: dict) -> LastSeenObjectId:
        return cls(json["lastSeenObjectId"], json["timestamp"])


@dataclasses.dataclass
class ReportHeapSnapshotProgress:
    """
    Attributes
    ----------
    done: int
    total: int
    finished: Optional[bool]
    """

    done: int
    total: int
    finished: Optional[bool] = None

    @classmethod
    def from_json(cls, json: dict) -> ReportHeapSnapshotProgress:
        return cls(json["done"], json["total"], json.get("finished"))


@dataclasses.dataclass
class ResetProfiles:
    """"""

    @classmethod
    def from_json(cls, json: dict) -> ResetProfiles:
        return cls()
