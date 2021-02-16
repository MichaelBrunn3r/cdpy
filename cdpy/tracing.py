from __future__ import annotations

import dataclasses
import enum
from typing import Generator, Optional

from . import io
from .common import filter_none


class MemoryDumpConfig(dict):
    """Configuration for memory dump. Used only when "memory-infra" category is enabled."""

    def __repr__(self):
        return f"MemoryDumpConfig({super().__repr__()})"


@dataclasses.dataclass
class TraceConfig:
    """
    Attributes
    ----------
    recordMode: Optional[str]
            Controls how the trace buffer stores data.
    enableSampling: Optional[bool]
            Turns on JavaScript stack sampling.
    enableSystrace: Optional[bool]
            Turns on system tracing.
    enableArgumentFilter: Optional[bool]
            Turns on argument filter.
    includedCategories: Optional[list[str]]
            Included category filters.
    excludedCategories: Optional[list[str]]
            Excluded category filters.
    syntheticDelays: Optional[list[str]]
            Configuration to synthesize the delays in tracing.
    memoryDumpConfig: Optional[MemoryDumpConfig]
            Configuration for memory dump triggers. Used only when "memory-infra" category is enabled.
    """

    recordMode: Optional[str] = None
    enableSampling: Optional[bool] = None
    enableSystrace: Optional[bool] = None
    enableArgumentFilter: Optional[bool] = None
    includedCategories: Optional[list[str]] = None
    excludedCategories: Optional[list[str]] = None
    syntheticDelays: Optional[list[str]] = None
    memoryDumpConfig: Optional[MemoryDumpConfig] = None

    @classmethod
    def from_json(cls, json: dict) -> TraceConfig:
        return cls(
            json.get("recordMode"),
            json.get("enableSampling"),
            json.get("enableSystrace"),
            json.get("enableArgumentFilter"),
            json.get("includedCategories"),
            json.get("excludedCategories"),
            json.get("syntheticDelays"),
            MemoryDumpConfig(json["memoryDumpConfig"])
            if "memoryDumpConfig" in json
            else None,
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "recordMode": self.recordMode,
                "enableSampling": self.enableSampling,
                "enableSystrace": self.enableSystrace,
                "enableArgumentFilter": self.enableArgumentFilter,
                "includedCategories": self.includedCategories,
                "excludedCategories": self.excludedCategories,
                "syntheticDelays": self.syntheticDelays,
                "memoryDumpConfig": dict(self.memoryDumpConfig)
                if self.memoryDumpConfig
                else None,
            }
        )


class StreamFormat(enum.Enum):
    """Data format of a trace. Can be either the legacy JSON format or the
    protocol buffer format. Note that the JSON format will be deprecated soon.
    """

    JSON = "json"
    PROTO = "proto"


class StreamCompression(enum.Enum):
    """Compression type to use for traces returned via streams."""

    NONE = "none"
    GZIP = "gzip"


class MemoryDumpLevelOfDetail(enum.Enum):
    """Details exposed when memory request explicitly declared.
    Keep consistent with memory_dump_request_args.h and
    memory_instrumentation.mojom
    """

    BACKGROUND = "background"
    LIGHT = "light"
    DETAILED = "detailed"


def end() -> dict:
    """Stop trace events collection."""
    return {"method": "Tracing.end", "params": {}}


def get_categories() -> Generator[dict, dict, list[str]]:
    """Gets supported tracing categories.

    Returns
    -------
    categories: list[str]
            A list of supported tracing categories.
    """
    response = yield {"method": "Tracing.getCategories", "params": {}}
    return response["categories"]


def record_clock_sync_marker(syncId: str) -> dict:
    """Record a clock sync marker in the trace.

    Parameters
    ----------
    syncId: str
            The ID of this clock sync marker
    """
    return {"method": "Tracing.recordClockSyncMarker", "params": {"syncId": syncId}}


def request_memory_dump(
    deterministic: Optional[bool] = None,
    levelOfDetail: Optional[MemoryDumpLevelOfDetail] = None,
) -> Generator[dict, dict, dict]:
    """Request a global memory dump.

    Parameters
    ----------
    deterministic: Optional[bool]
            Enables more deterministic results by forcing garbage collection
    levelOfDetail: Optional[MemoryDumpLevelOfDetail]
            Specifies level of details in memory dump. Defaults to "detailed".

    Returns
    -------
    dumpGuid: str
            GUID of the resulting global memory dump.
    success: bool
            True iff the global memory dump succeeded.
    """
    response = yield {
        "method": "Tracing.requestMemoryDump",
        "params": filter_none(
            {
                "deterministic": deterministic,
                "levelOfDetail": levelOfDetail.value if levelOfDetail else None,
            }
        ),
    }
    return {"dumpGuid": response["dumpGuid"], "success": response["success"]}


def start(
    categories: Optional[str] = None,
    options: Optional[str] = None,
    bufferUsageReportingInterval: Optional[float] = None,
    transferMode: Optional[str] = None,
    streamFormat: Optional[StreamFormat] = None,
    streamCompression: Optional[StreamCompression] = None,
    traceConfig: Optional[TraceConfig] = None,
    perfettoConfig: Optional[str] = None,
) -> dict:
    """Start trace events collection.

    Parameters
    ----------
    categories: Optional[str]
            Category/tag filter
    options: Optional[str]
            Tracing options
    bufferUsageReportingInterval: Optional[float]
            If set, the agent will issue bufferUsage events at this interval, specified in milliseconds
    transferMode: Optional[str]
            Whether to report trace events as series of dataCollected events or to save trace to a
            stream (defaults to `ReportEvents`).
    streamFormat: Optional[StreamFormat]
            Trace data format to use. This only applies when using `ReturnAsStream`
            transfer mode (defaults to `json`).
    streamCompression: Optional[StreamCompression]
            Compression format to use. This only applies when using `ReturnAsStream`
            transfer mode (defaults to `none`)
    traceConfig: Optional[TraceConfig]
    perfettoConfig: Optional[str]
            Base64-encoded serialized perfetto.protos.TraceConfig protobuf message
            When specified, the parameters `categories`, `options`, `traceConfig`
            are ignored. (Encoded as a base64 string when passed over JSON)
    """
    return {
        "method": "Tracing.start",
        "params": filter_none(
            {
                "categories": categories,
                "options": options,
                "bufferUsageReportingInterval": bufferUsageReportingInterval,
                "transferMode": transferMode,
                "streamFormat": streamFormat.value if streamFormat else None,
                "streamCompression": streamCompression.value
                if streamCompression
                else None,
                "traceConfig": traceConfig.to_json() if traceConfig else None,
                "perfettoConfig": perfettoConfig,
            }
        ),
    }


@dataclasses.dataclass
class BufferUsage:
    """
    Attributes
    ----------
    percentFull: Optional[float]
            A number in range [0..1] that indicates the used size of event buffer as a fraction of its
            total size.
    eventCount: Optional[float]
            An approximate number of events in the trace log.
    value: Optional[float]
            A number in range [0..1] that indicates the used size of event buffer as a fraction of its
            total size.
    """

    percentFull: Optional[float] = None
    eventCount: Optional[float] = None
    value: Optional[float] = None

    @classmethod
    def from_json(cls, json: dict) -> BufferUsage:
        return cls(json.get("percentFull"), json.get("eventCount"), json.get("value"))


@dataclasses.dataclass
class DataCollected:
    """Contains an bucket of collected trace events. When tracing is stopped collected events will be
    send as a sequence of dataCollected events followed by tracingComplete event.

    Attributes
    ----------
    value: list[dict]
    """

    value: list[dict]

    @classmethod
    def from_json(cls, json: dict) -> DataCollected:
        return cls(json["value"])


@dataclasses.dataclass
class TracingComplete:
    """Signals that tracing is stopped and there is no trace buffers pending flush, all data were
    delivered via dataCollected events.

    Attributes
    ----------
    dataLossOccurred: bool
            Indicates whether some trace data is known to have been lost, e.g. because the trace ring
            buffer wrapped around.
    stream: Optional[io.StreamHandle]
            A handle of the stream that holds resulting trace data.
    traceFormat: Optional[StreamFormat]
            Trace data format of returned stream.
    streamCompression: Optional[StreamCompression]
            Compression format of returned stream.
    """

    dataLossOccurred: bool
    stream: Optional[io.StreamHandle] = None
    traceFormat: Optional[StreamFormat] = None
    streamCompression: Optional[StreamCompression] = None

    @classmethod
    def from_json(cls, json: dict) -> TracingComplete:
        return cls(
            json["dataLossOccurred"],
            io.StreamHandle(json["stream"]) if "stream" in json else None,
            StreamFormat(json["traceFormat"]) if "traceFormat" in json else None,
            StreamCompression(json["streamCompression"])
            if "streamCompression" in json
            else None,
        )
