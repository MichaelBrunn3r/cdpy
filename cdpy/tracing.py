from __future__ import annotations

import dataclasses
import enum
from typing import Optional

from .common import filter_unset_parameters


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


def end():
    """Stop trace events collection."""
    return {"method": "Tracing.end", "params": {}}


def get_categories():
    """Gets supported tracing categories.

    Returns
    -------
    categories: list[str]
            A list of supported tracing categories.
    """
    return {"method": "Tracing.getCategories", "params": {}}


def record_clock_sync_marker(syncId: str):
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
):
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
    return filter_unset_parameters(
        {
            "method": "Tracing.requestMemoryDump",
            "params": {"deterministic": deterministic, "levelOfDetail": levelOfDetail},
        }
    )


def start(
    categories: Optional[str] = None,
    options: Optional[str] = None,
    bufferUsageReportingInterval: Optional[float] = None,
    transferMode: Optional[str] = None,
    streamFormat: Optional[StreamFormat] = None,
    streamCompression: Optional[StreamCompression] = None,
    traceConfig: Optional[TraceConfig] = None,
    perfettoConfig: Optional[str] = None,
):
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
    return filter_unset_parameters(
        {
            "method": "Tracing.start",
            "params": {
                "categories": categories,
                "options": options,
                "bufferUsageReportingInterval": bufferUsageReportingInterval,
                "transferMode": transferMode,
                "streamFormat": streamFormat,
                "streamCompression": streamCompression,
                "traceConfig": traceConfig,
                "perfettoConfig": perfettoConfig,
            },
        }
    )
