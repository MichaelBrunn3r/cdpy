from __future__ import annotations

import dataclasses
from typing import Generator, Optional

from . import debugger, runtime
from .common import filter_none


@dataclasses.dataclass
class ProfileNode:
    """Profile node. Holds callsite information, execution statistics and child nodes.

    Attributes
    ----------
    id: int
            Unique id of the node.
    callFrame: runtime.CallFrame
            Function location.
    hitCount: Optional[int]
            Number of samples where this node was on top of the call stack.
    children: Optional[list[int]]
            Child node ids.
    deoptReason: Optional[str]
            The reason of being not optimized. The function may be deoptimized or marked as don't
            optimize.
    positionTicks: Optional[list[PositionTickInfo]]
            An array of source position ticks.
    """

    id: int
    callFrame: runtime.CallFrame
    hitCount: Optional[int] = None
    children: Optional[list[int]] = None
    deoptReason: Optional[str] = None
    positionTicks: Optional[list[PositionTickInfo]] = None

    @classmethod
    def from_json(cls, json: dict) -> ProfileNode:
        return cls(
            json["id"],
            runtime.CallFrame.from_json(json["callFrame"]),
            json.get("hitCount"),
            json.get("children"),
            json.get("deoptReason"),
            [PositionTickInfo.from_json(p) for p in json["positionTicks"]]
            if "positionTicks" in json
            else None,
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "id": self.id,
                "callFrame": self.callFrame.to_json(),
                "hitCount": self.hitCount,
                "children": self.children,
                "deoptReason": self.deoptReason,
                "positionTicks": [p.to_json() for p in self.positionTicks]
                if self.positionTicks
                else None,
            }
        )


@dataclasses.dataclass
class Profile:
    """Profile.

    Attributes
    ----------
    nodes: list[ProfileNode]
            The list of profile nodes. First item is the root node.
    startTime: float
            Profiling start timestamp in microseconds.
    endTime: float
            Profiling end timestamp in microseconds.
    samples: Optional[list[int]]
            Ids of samples top nodes.
    timeDeltas: Optional[list[int]]
            Time intervals between adjacent samples in microseconds. The first delta is relative to the
            profile startTime.
    """

    nodes: list[ProfileNode]
    startTime: float
    endTime: float
    samples: Optional[list[int]] = None
    timeDeltas: Optional[list[int]] = None

    @classmethod
    def from_json(cls, json: dict) -> Profile:
        return cls(
            [ProfileNode.from_json(n) for n in json["nodes"]],
            json["startTime"],
            json["endTime"],
            json.get("samples"),
            json.get("timeDeltas"),
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "nodes": [n.to_json() for n in self.nodes],
                "startTime": self.startTime,
                "endTime": self.endTime,
                "samples": self.samples,
                "timeDeltas": self.timeDeltas,
            }
        )


@dataclasses.dataclass
class PositionTickInfo:
    """Specifies a number of samples attributed to a certain source position.

    Attributes
    ----------
    line: int
            Source line number (1-based).
    ticks: int
            Number of samples attributed to the source line.
    """

    line: int
    ticks: int

    @classmethod
    def from_json(cls, json: dict) -> PositionTickInfo:
        return cls(json["line"], json["ticks"])

    def to_json(self) -> dict:
        return {"line": self.line, "ticks": self.ticks}


@dataclasses.dataclass
class CoverageRange:
    """Coverage data for a source range.

    Attributes
    ----------
    startOffset: int
            JavaScript script source offset for the range start.
    endOffset: int
            JavaScript script source offset for the range end.
    count: int
            Collected execution count of the source range.
    """

    startOffset: int
    endOffset: int
    count: int

    @classmethod
    def from_json(cls, json: dict) -> CoverageRange:
        return cls(json["startOffset"], json["endOffset"], json["count"])

    def to_json(self) -> dict:
        return {
            "startOffset": self.startOffset,
            "endOffset": self.endOffset,
            "count": self.count,
        }


@dataclasses.dataclass
class FunctionCoverage:
    """Coverage data for a JavaScript function.

    Attributes
    ----------
    functionName: str
            JavaScript function name.
    ranges: list[CoverageRange]
            Source ranges inside the function with coverage data.
    isBlockCoverage: bool
            Whether coverage data for this function has block granularity.
    """

    functionName: str
    ranges: list[CoverageRange]
    isBlockCoverage: bool

    @classmethod
    def from_json(cls, json: dict) -> FunctionCoverage:
        return cls(
            json["functionName"],
            [CoverageRange.from_json(r) for r in json["ranges"]],
            json["isBlockCoverage"],
        )

    def to_json(self) -> dict:
        return {
            "functionName": self.functionName,
            "ranges": [r.to_json() for r in self.ranges],
            "isBlockCoverage": self.isBlockCoverage,
        }


@dataclasses.dataclass
class ScriptCoverage:
    """Coverage data for a JavaScript script.

    Attributes
    ----------
    scriptId: runtime.ScriptId
            JavaScript script id.
    url: str
            JavaScript script name or url.
    functions: list[FunctionCoverage]
            Functions contained in the script that has coverage data.
    """

    scriptId: runtime.ScriptId
    url: str
    functions: list[FunctionCoverage]

    @classmethod
    def from_json(cls, json: dict) -> ScriptCoverage:
        return cls(
            runtime.ScriptId(json["scriptId"]),
            json["url"],
            [FunctionCoverage.from_json(f) for f in json["functions"]],
        )

    def to_json(self) -> dict:
        return {
            "scriptId": str(self.scriptId),
            "url": self.url,
            "functions": [f.to_json() for f in self.functions],
        }


@dataclasses.dataclass
class TypeObject:
    """Describes a type collected during runtime.

    Attributes
    ----------
    name: str
            Name of a type collected with type profiling.
    """

    name: str

    @classmethod
    def from_json(cls, json: dict) -> TypeObject:
        return cls(json["name"])

    def to_json(self) -> dict:
        return {"name": self.name}


@dataclasses.dataclass
class TypeProfileEntry:
    """Source offset and types for a parameter or return value.

    Attributes
    ----------
    offset: int
            Source offset of the parameter or end of function for return values.
    types: list[TypeObject]
            The types for this parameter or return value.
    """

    offset: int
    types: list[TypeObject]

    @classmethod
    def from_json(cls, json: dict) -> TypeProfileEntry:
        return cls(json["offset"], [TypeObject.from_json(t) for t in json["types"]])

    def to_json(self) -> dict:
        return {"offset": self.offset, "types": [t.to_json() for t in self.types]}


@dataclasses.dataclass
class ScriptTypeProfile:
    """Type profile data collected during runtime for a JavaScript script.

    Attributes
    ----------
    scriptId: runtime.ScriptId
            JavaScript script id.
    url: str
            JavaScript script name or url.
    entries: list[TypeProfileEntry]
            Type profile entries for parameters and return values of the functions in the script.
    """

    scriptId: runtime.ScriptId
    url: str
    entries: list[TypeProfileEntry]

    @classmethod
    def from_json(cls, json: dict) -> ScriptTypeProfile:
        return cls(
            runtime.ScriptId(json["scriptId"]),
            json["url"],
            [TypeProfileEntry.from_json(e) for e in json["entries"]],
        )

    def to_json(self) -> dict:
        return {
            "scriptId": str(self.scriptId),
            "url": self.url,
            "entries": [e.to_json() for e in self.entries],
        }


@dataclasses.dataclass
class CounterInfo:
    """Collected counter information.

    Attributes
    ----------
    name: str
            Counter name.
    value: int
            Counter value.
    """

    name: str
    value: int

    @classmethod
    def from_json(cls, json: dict) -> CounterInfo:
        return cls(json["name"], json["value"])

    def to_json(self) -> dict:
        return {"name": self.name, "value": self.value}


@dataclasses.dataclass
class RuntimeCallCounterInfo:
    """Runtime call counter information.

    Attributes
    ----------
    name: str
            Counter name.
    value: float
            Counter value.
    time: float
            Counter time in seconds.
    """

    name: str
    value: float
    time: float

    @classmethod
    def from_json(cls, json: dict) -> RuntimeCallCounterInfo:
        return cls(json["name"], json["value"], json["time"])

    def to_json(self) -> dict:
        return {"name": self.name, "value": self.value, "time": self.time}


def disable() -> dict:
    """"""
    return {"method": "Profiler.disable", "params": {}}


def enable() -> dict:
    """"""
    return {"method": "Profiler.enable", "params": {}}


def get_best_effort_coverage() -> Generator[dict, dict, list[ScriptCoverage]]:
    """Collect coverage data for the current isolate. The coverage data may be incomplete due to
    garbage collection.

    Returns
    -------
    result: list[ScriptCoverage]
            Coverage data for the current isolate.
    """
    response = yield {"method": "Profiler.getBestEffortCoverage", "params": {}}
    return [ScriptCoverage.from_json(r) for r in response["result"]]


def set_sampling_interval(interval: int) -> dict:
    """Changes CPU profiler sampling interval. Must be called before CPU profiles recording started.

    Parameters
    ----------
    interval: int
            New sampling interval in microseconds.
    """
    return {"method": "Profiler.setSamplingInterval", "params": {"interval": interval}}


def start() -> dict:
    """"""
    return {"method": "Profiler.start", "params": {}}


def start_precise_coverage(
    callCount: Optional[bool] = None,
    detailed: Optional[bool] = None,
    allowTriggeredUpdates: Optional[bool] = None,
) -> Generator[dict, dict, float]:
    """Enable precise code coverage. Coverage data for JavaScript executed before enabling precise code
    coverage may be incomplete. Enabling prevents running optimized code and resets execution
    counters.

    Parameters
    ----------
    callCount: Optional[bool]
            Collect accurate call counts beyond simple 'covered' or 'not covered'.
    detailed: Optional[bool]
            Collect block-based coverage.
    allowTriggeredUpdates: Optional[bool]
            Allow the backend to send updates on its own initiative

    Returns
    -------
    timestamp: float
            Monotonically increasing time (in seconds) when the coverage update was taken in the backend.
    """
    response = yield {
        "method": "Profiler.startPreciseCoverage",
        "params": filter_none(
            {
                "callCount": callCount,
                "detailed": detailed,
                "allowTriggeredUpdates": allowTriggeredUpdates,
            }
        ),
    }
    return response["timestamp"]


def start_type_profile() -> dict:
    """Enable type profile.

    **Experimental**
    """
    return {"method": "Profiler.startTypeProfile", "params": {}}


def stop() -> Generator[dict, dict, Profile]:
    """
    Returns
    -------
    profile: Profile
            Recorded profile.
    """
    response = yield {"method": "Profiler.stop", "params": {}}
    return Profile.from_json(response["profile"])


def stop_precise_coverage() -> dict:
    """Disable precise code coverage. Disabling releases unnecessary execution count records and allows
    executing optimized code.
    """
    return {"method": "Profiler.stopPreciseCoverage", "params": {}}


def stop_type_profile() -> dict:
    """Disable type profile. Disabling releases type profile data collected so far.

    **Experimental**
    """
    return {"method": "Profiler.stopTypeProfile", "params": {}}


def take_precise_coverage() -> Generator[dict, dict, dict]:
    """Collect coverage data for the current isolate, and resets execution counters. Precise code
    coverage needs to have started.

    Returns
    -------
    result: list[ScriptCoverage]
            Coverage data for the current isolate.
    timestamp: float
            Monotonically increasing time (in seconds) when the coverage update was taken in the backend.
    """
    response = yield {"method": "Profiler.takePreciseCoverage", "params": {}}
    return {
        "result": [ScriptCoverage.from_json(r) for r in response["result"]],
        "timestamp": response["timestamp"],
    }


def take_type_profile() -> Generator[dict, dict, list[ScriptTypeProfile]]:
    """Collect type profile.

    Returns
    -------
    result: list[ScriptTypeProfile]
            Type profile for all scripts since startTypeProfile() was turned on.

    **Experimental**
    """
    response = yield {"method": "Profiler.takeTypeProfile", "params": {}}
    return [ScriptTypeProfile.from_json(r) for r in response["result"]]


def enable_counters() -> dict:
    """Enable counters collection.

    **Experimental**
    """
    return {"method": "Profiler.enableCounters", "params": {}}


def disable_counters() -> dict:
    """Disable counters collection.

    **Experimental**
    """
    return {"method": "Profiler.disableCounters", "params": {}}


def get_counters() -> Generator[dict, dict, list[CounterInfo]]:
    """Retrieve counters.

    Returns
    -------
    result: list[CounterInfo]
            Collected counters information.

    **Experimental**
    """
    response = yield {"method": "Profiler.getCounters", "params": {}}
    return [CounterInfo.from_json(r) for r in response["result"]]


def enable_runtime_call_stats() -> dict:
    """Enable run time call stats collection.

    **Experimental**
    """
    return {"method": "Profiler.enableRuntimeCallStats", "params": {}}


def disable_runtime_call_stats() -> dict:
    """Disable run time call stats collection.

    **Experimental**
    """
    return {"method": "Profiler.disableRuntimeCallStats", "params": {}}


def get_runtime_call_stats() -> Generator[dict, dict, list[RuntimeCallCounterInfo]]:
    """Retrieve run time call stats.

    Returns
    -------
    result: list[RuntimeCallCounterInfo]
            Collected runtime call counter information.

    **Experimental**
    """
    response = yield {"method": "Profiler.getRuntimeCallStats", "params": {}}
    return [RuntimeCallCounterInfo.from_json(r) for r in response["result"]]


@dataclasses.dataclass
class ConsoleProfileFinished:
    """
    Attributes
    ----------
    id: str
    location: debugger.Location
            Location of console.profileEnd().
    profile: Profile
    title: Optional[str]
            Profile title passed as an argument to console.profile().
    """

    id: str
    location: debugger.Location
    profile: Profile
    title: Optional[str] = None

    @classmethod
    def from_json(cls, json: dict) -> ConsoleProfileFinished:
        return cls(
            json["id"],
            debugger.Location.from_json(json["location"]),
            Profile.from_json(json["profile"]),
            json.get("title"),
        )


@dataclasses.dataclass
class ConsoleProfileStarted:
    """Sent when new profile recording is started using console.profile() call.

    Attributes
    ----------
    id: str
    location: debugger.Location
            Location of console.profile().
    title: Optional[str]
            Profile title passed as an argument to console.profile().
    """

    id: str
    location: debugger.Location
    title: Optional[str] = None

    @classmethod
    def from_json(cls, json: dict) -> ConsoleProfileStarted:
        return cls(
            json["id"], debugger.Location.from_json(json["location"]), json.get("title")
        )


@dataclasses.dataclass
class PreciseCoverageDeltaUpdate:
    """Reports coverage delta since the last poll (either from an event like this, or from
    `takePreciseCoverage` for the current isolate. May only be sent if precise code
    coverage has been started. This event can be trigged by the embedder to, for example,
    trigger collection of coverage data immediatelly at a certain point in time.

    Attributes
    ----------
    timestamp: float
            Monotonically increasing time (in seconds) when the coverage update was taken in the backend.
    occassion: str
            Identifier for distinguishing coverage events.
    result: list[ScriptCoverage]
            Coverage data for the current isolate.
    """

    timestamp: float
    occassion: str
    result: list[ScriptCoverage]

    @classmethod
    def from_json(cls, json: dict) -> PreciseCoverageDeltaUpdate:
        return cls(
            json["timestamp"],
            json["occassion"],
            [ScriptCoverage.from_json(r) for r in json["result"]],
        )
