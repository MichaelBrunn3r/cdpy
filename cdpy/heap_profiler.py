from __future__ import annotations

import dataclasses
import enum
from typing import Optional

from . import runtime
from .common import Type, filter_unset_parameters


class HeapSnapshotObjectId(str):
    """Heap snapshot object id."""

    def __repr__(self):
        return f"HeapSnapshotObjectId({super().__repr__()})"


@dataclasses.dataclass
class SamplingHeapProfileNode(Type):
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
            [SamplingHeapProfileNode.from_json(x) for x in json["children"]],
        )


@dataclasses.dataclass
class SamplingHeapProfileSample(Type):
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


@dataclasses.dataclass
class SamplingHeapProfile(Type):
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
            [SamplingHeapProfileSample.from_json(x) for x in json["samples"]],
        )


def add_inspected_heap_object(heapObjectId: HeapSnapshotObjectId):
    """Enables console to refer to the node with given id via $x (see Command Line API for more details
    $x functions).

    Parameters
    ----------
    heapObjectId: HeapSnapshotObjectId
            Heap snapshot object id to be accessible by means of $x command line API.
    """
    return {
        "method": "HeapProfiler.addInspectedHeapObject",
        "params": {"heapObjectId": heapObjectId},
    }


def collect_garbage():
    """"""
    return {"method": "HeapProfiler.collectGarbage", "params": {}}


def disable():
    """"""
    return {"method": "HeapProfiler.disable", "params": {}}


def enable():
    """"""
    return {"method": "HeapProfiler.enable", "params": {}}


def get_heap_object_id(objectId: runtime.RemoteObjectId):
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
    return {"method": "HeapProfiler.getHeapObjectId", "params": {"objectId": objectId}}


def get_object_by_heap_object_id(
    objectId: HeapSnapshotObjectId, objectGroup: Optional[str] = None
):
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
    return filter_unset_parameters(
        {
            "method": "HeapProfiler.getObjectByHeapObjectId",
            "params": {"objectId": objectId, "objectGroup": objectGroup},
        }
    )


def get_sampling_profile():
    """
    Returns
    -------
    profile: SamplingHeapProfile
            Return the sampling profile being collected.
    """
    return {"method": "HeapProfiler.getSamplingProfile", "params": {}}


def start_sampling(samplingInterval: Optional[float] = None):
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


def start_tracking_heap_objects(trackAllocations: Optional[bool] = None):
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


def stop_sampling():
    """
    Returns
    -------
    profile: SamplingHeapProfile
            Recorded sampling heap profile.
    """
    return {"method": "HeapProfiler.stopSampling", "params": {}}


def stop_tracking_heap_objects(
    reportProgress: Optional[bool] = None,
    treatGlobalObjectsAsRoots: Optional[bool] = None,
):
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
):
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
