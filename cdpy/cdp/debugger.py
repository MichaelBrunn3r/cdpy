from __future__ import annotations

import dataclasses
import enum
from typing import Generator, Optional

from deprecated.sphinx import deprecated

from . import runtime
from ._utils import filter_none


class BreakpointId(str):
    """Breakpoint identifier."""

    def __repr__(self):
        return f"BreakpointId({super().__repr__()})"


class CallFrameId(str):
    """Call frame identifier."""

    def __repr__(self):
        return f"CallFrameId({super().__repr__()})"


@dataclasses.dataclass
class Location:
    """Location in the source code.

    Attributes
    ----------
    scriptId: runtime.ScriptId
            Script identifier as reported in the `Debugger.scriptParsed`.
    lineNumber: int
            Line number in the script (0-based).
    columnNumber: Optional[int]
            Column number in the script (0-based).
    """

    scriptId: runtime.ScriptId
    lineNumber: int
    columnNumber: Optional[int] = None

    @classmethod
    def from_json(cls, json: dict) -> Location:
        return cls(
            runtime.ScriptId(json["scriptId"]),
            json["lineNumber"],
            json.get("columnNumber"),
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "scriptId": str(self.scriptId),
                "lineNumber": self.lineNumber,
                "columnNumber": self.columnNumber,
            }
        )


@dataclasses.dataclass
class ScriptPosition:
    """Location in the source code.

    Attributes
    ----------
    lineNumber: int
    columnNumber: int
    """

    lineNumber: int
    columnNumber: int

    @classmethod
    def from_json(cls, json: dict) -> ScriptPosition:
        return cls(json["lineNumber"], json["columnNumber"])

    def to_json(self) -> dict:
        return {"lineNumber": self.lineNumber, "columnNumber": self.columnNumber}


@dataclasses.dataclass
class LocationRange:
    """Location range within one script.

    Attributes
    ----------
    scriptId: runtime.ScriptId
    start: ScriptPosition
    end: ScriptPosition
    """

    scriptId: runtime.ScriptId
    start: ScriptPosition
    end: ScriptPosition

    @classmethod
    def from_json(cls, json: dict) -> LocationRange:
        return cls(
            runtime.ScriptId(json["scriptId"]),
            ScriptPosition.from_json(json["start"]),
            ScriptPosition.from_json(json["end"]),
        )

    def to_json(self) -> dict:
        return {
            "scriptId": str(self.scriptId),
            "start": self.start.to_json(),
            "end": self.end.to_json(),
        }


@dataclasses.dataclass
class CallFrame:
    """JavaScript call frame. Array of call frames form the call stack.

    Attributes
    ----------
    callFrameId: CallFrameId
            Call frame identifier. This identifier is only valid while the virtual machine is paused.
    functionName: str
            Name of the JavaScript function called on this call frame.
    location: Location
            Location in the source code.
    url: str
            JavaScript script name or url.
    scopeChain: list[Scope]
            Scope chain for this call frame.
    this: runtime.RemoteObject
            `this` object for this call frame.
    functionLocation: Optional[Location]
            Location in the source code.
    returnValue: Optional[runtime.RemoteObject]
            The value being returned, if the function is at return point.
    """

    callFrameId: CallFrameId
    functionName: str
    location: Location
    url: str
    scopeChain: list[Scope]
    this: runtime.RemoteObject
    functionLocation: Optional[Location] = None
    returnValue: Optional[runtime.RemoteObject] = None

    @classmethod
    def from_json(cls, json: dict) -> CallFrame:
        return cls(
            CallFrameId(json["callFrameId"]),
            json["functionName"],
            Location.from_json(json["location"]),
            json["url"],
            [Scope.from_json(s) for s in json["scopeChain"]],
            runtime.RemoteObject.from_json(json["this"]),
            Location.from_json(json["functionLocation"])
            if "functionLocation" in json
            else None,
            runtime.RemoteObject.from_json(json["returnValue"])
            if "returnValue" in json
            else None,
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "callFrameId": str(self.callFrameId),
                "functionName": self.functionName,
                "location": self.location.to_json(),
                "url": self.url,
                "scopeChain": [s.to_json() for s in self.scopeChain],
                "this": self.this.to_json(),
                "functionLocation": self.functionLocation.to_json()
                if self.functionLocation
                else None,
                "returnValue": self.returnValue.to_json() if self.returnValue else None,
            }
        )


@dataclasses.dataclass
class Scope:
    """Scope description.

    Attributes
    ----------
    type: str
            Scope type.
    object: runtime.RemoteObject
            Object representing the scope. For `global` and `with` scopes it represents the actual
            object; for the rest of the scopes, it is artificial transient object enumerating scope
            variables as its properties.
    name: Optional[str]
    startLocation: Optional[Location]
            Location in the source code where scope starts
    endLocation: Optional[Location]
            Location in the source code where scope ends
    """

    type: str
    object: runtime.RemoteObject
    name: Optional[str] = None
    startLocation: Optional[Location] = None
    endLocation: Optional[Location] = None

    @classmethod
    def from_json(cls, json: dict) -> Scope:
        return cls(
            json["type"],
            runtime.RemoteObject.from_json(json["object"]),
            json.get("name"),
            Location.from_json(json["startLocation"])
            if "startLocation" in json
            else None,
            Location.from_json(json["endLocation"]) if "endLocation" in json else None,
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "type": self.type,
                "object": self.object.to_json(),
                "name": self.name,
                "startLocation": self.startLocation.to_json()
                if self.startLocation
                else None,
                "endLocation": self.endLocation.to_json() if self.endLocation else None,
            }
        )


@dataclasses.dataclass
class SearchMatch:
    """Search match for resource.

    Attributes
    ----------
    lineNumber: float
            Line number in resource content.
    lineContent: str
            Line with match content.
    """

    lineNumber: float
    lineContent: str

    @classmethod
    def from_json(cls, json: dict) -> SearchMatch:
        return cls(json["lineNumber"], json["lineContent"])

    def to_json(self) -> dict:
        return {"lineNumber": self.lineNumber, "lineContent": self.lineContent}


@dataclasses.dataclass
class BreakLocation:
    """
    Attributes
    ----------
    scriptId: runtime.ScriptId
            Script identifier as reported in the `Debugger.scriptParsed`.
    lineNumber: int
            Line number in the script (0-based).
    columnNumber: Optional[int]
            Column number in the script (0-based).
    type: Optional[str]
    """

    scriptId: runtime.ScriptId
    lineNumber: int
    columnNumber: Optional[int] = None
    type: Optional[str] = None

    @classmethod
    def from_json(cls, json: dict) -> BreakLocation:
        return cls(
            runtime.ScriptId(json["scriptId"]),
            json["lineNumber"],
            json.get("columnNumber"),
            json.get("type"),
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "scriptId": str(self.scriptId),
                "lineNumber": self.lineNumber,
                "columnNumber": self.columnNumber,
                "type": self.type,
            }
        )


class ScriptLanguage(enum.Enum):
    """Enum of possible script languages."""

    JAVA_SCRIPT = "JavaScript"
    WEB_ASSEMBLY = "WebAssembly"


@dataclasses.dataclass
class DebugSymbols:
    """Debug symbols available for a wasm script.

    Attributes
    ----------
    type: str
            Type of the debug symbols.
    externalURL: Optional[str]
            URL of the external symbol source.
    """

    type: str
    externalURL: Optional[str] = None

    @classmethod
    def from_json(cls, json: dict) -> DebugSymbols:
        return cls(json["type"], json.get("externalURL"))

    def to_json(self) -> dict:
        return filter_none({"type": self.type, "externalURL": self.externalURL})


def continue_to_location(
    location: Location, targetCallFrames: Optional[str] = None
) -> dict:
    """Continues execution until specific location is reached.

    Parameters
    ----------
    location: Location
            Location to continue to.
    targetCallFrames: Optional[str]
    """
    return {
        "method": "Debugger.continueToLocation",
        "params": filter_none(
            {"location": location.to_json(), "targetCallFrames": targetCallFrames}
        ),
    }


def disable() -> dict:
    """Disables debugger for given page."""
    return {"method": "Debugger.disable", "params": {}}


def enable(
    maxScriptsCacheSize: Optional[float] = None,
) -> Generator[dict, dict, runtime.UniqueDebuggerId]:
    """Enables debugger for the given page. Clients should not assume that the debugging has been
    enabled until the result for this command is received.

    Parameters
    ----------
    maxScriptsCacheSize: Optional[float]
            The maximum size in bytes of collected scripts (not referenced by other heap objects)
            the debugger can hold. Puts no limit if paramter is omitted.

    Returns
    -------
    debuggerId: runtime.UniqueDebuggerId
            Unique identifier of the debugger.
    """
    response = yield {
        "method": "Debugger.enable",
        "params": filter_none({"maxScriptsCacheSize": maxScriptsCacheSize}),
    }
    return runtime.UniqueDebuggerId(response["debuggerId"])


def evaluate_on_call_frame(
    callFrameId: CallFrameId,
    expression: str,
    objectGroup: Optional[str] = None,
    includeCommandLineAPI: Optional[bool] = None,
    silent: Optional[bool] = None,
    returnByValue: Optional[bool] = None,
    generatePreview: Optional[bool] = None,
    throwOnSideEffect: Optional[bool] = None,
    timeout: Optional[runtime.TimeDelta] = None,
) -> Generator[dict, dict, dict]:
    """Evaluates expression on a given call frame.

    Parameters
    ----------
    callFrameId: CallFrameId
            Call frame identifier to evaluate on.
    expression: str
            Expression to evaluate.
    objectGroup: Optional[str]
            String object group name to put result into (allows rapid releasing resulting object handles
            using `releaseObjectGroup`).
    includeCommandLineAPI: Optional[bool]
            Specifies whether command line API should be available to the evaluated expression, defaults
            to false.
    silent: Optional[bool]
            In silent mode exceptions thrown during evaluation are not reported and do not pause
            execution. Overrides `setPauseOnException` state.
    returnByValue: Optional[bool]
            Whether the result is expected to be a JSON object that should be sent by value.
    generatePreview: Optional[bool]
            Whether preview should be generated for the result.
    throwOnSideEffect: Optional[bool]
            Whether to throw an exception if side effect cannot be ruled out during evaluation.
    timeout: Optional[runtime.TimeDelta]
            Terminate execution after timing out (number of milliseconds).

    Returns
    -------
    result: runtime.RemoteObject
            Object wrapper for the evaluation result.
    exceptionDetails: Optional[runtime.ExceptionDetails]
            Exception details.
    """
    response = yield {
        "method": "Debugger.evaluateOnCallFrame",
        "params": filter_none(
            {
                "callFrameId": str(callFrameId),
                "expression": expression,
                "objectGroup": objectGroup,
                "includeCommandLineAPI": includeCommandLineAPI,
                "silent": silent,
                "returnByValue": returnByValue,
                "generatePreview": generatePreview,
                "throwOnSideEffect": throwOnSideEffect,
                "timeout": float(timeout) if timeout else None,
            }
        ),
    }
    return {
        "result": runtime.RemoteObject.from_json(response["result"]),
        "exceptionDetails": runtime.ExceptionDetails.from_json(
            response["exceptionDetails"]
        )
        if "exceptionDetails" in response
        else None,
    }


def execute_wasm_evaluator(
    callFrameId: CallFrameId,
    evaluator: str,
    timeout: Optional[runtime.TimeDelta] = None,
) -> Generator[dict, dict, dict]:
    """Execute a Wasm Evaluator module on a given call frame.

    Parameters
    ----------
    callFrameId: CallFrameId
            WebAssembly call frame identifier to evaluate on.
    evaluator: str
            Code of the evaluator module. (Encoded as a base64 string when passed over JSON)
    timeout: Optional[runtime.TimeDelta]
            Terminate execution after timing out (number of milliseconds).

    Returns
    -------
    result: runtime.RemoteObject
            Object wrapper for the evaluation result.
    exceptionDetails: Optional[runtime.ExceptionDetails]
            Exception details.

    **Experimental**
    """
    response = yield {
        "method": "Debugger.executeWasmEvaluator",
        "params": filter_none(
            {
                "callFrameId": str(callFrameId),
                "evaluator": evaluator,
                "timeout": float(timeout) if timeout else None,
            }
        ),
    }
    return {
        "result": runtime.RemoteObject.from_json(response["result"]),
        "exceptionDetails": runtime.ExceptionDetails.from_json(
            response["exceptionDetails"]
        )
        if "exceptionDetails" in response
        else None,
    }


def get_possible_breakpoints(
    start: Location,
    end: Optional[Location] = None,
    restrictToFunction: Optional[bool] = None,
) -> Generator[dict, dict, list[BreakLocation]]:
    """Returns possible locations for breakpoint. scriptId in start and end range locations should be
    the same.

    Parameters
    ----------
    start: Location
            Start of range to search possible breakpoint locations in.
    end: Optional[Location]
            End of range to search possible breakpoint locations in (excluding). When not specified, end
            of scripts is used as end of range.
    restrictToFunction: Optional[bool]
            Only consider locations which are in the same (non-nested) function as start.

    Returns
    -------
    locations: list[BreakLocation]
            List of the possible breakpoint locations.
    """
    response = yield {
        "method": "Debugger.getPossibleBreakpoints",
        "params": filter_none(
            {
                "start": start.to_json(),
                "end": end.to_json() if end else None,
                "restrictToFunction": restrictToFunction,
            }
        ),
    }
    return [BreakLocation.from_json(l) for l in response["locations"]]


def get_script_source(scriptId: runtime.ScriptId) -> Generator[dict, dict, dict]:
    """Returns source for the script with given id.

    Parameters
    ----------
    scriptId: runtime.ScriptId
            Id of the script to get source for.

    Returns
    -------
    scriptSource: str
            Script source (empty in case of Wasm bytecode).
    bytecode: Optional[str]
            Wasm bytecode. (Encoded as a base64 string when passed over JSON)
    """
    response = yield {
        "method": "Debugger.getScriptSource",
        "params": {"scriptId": str(scriptId)},
    }
    return {
        "scriptSource": response["scriptSource"],
        "bytecode": response.get("bytecode"),
    }


@deprecated(version=1.3)
def get_wasm_bytecode(scriptId: runtime.ScriptId) -> Generator[dict, dict, str]:
    """This command is deprecated. Use getScriptSource instead.

    Parameters
    ----------
    scriptId: runtime.ScriptId
            Id of the Wasm script to get source for.

    Returns
    -------
    bytecode: str
            Script source. (Encoded as a base64 string when passed over JSON)
    """
    response = yield {
        "method": "Debugger.getWasmBytecode",
        "params": {"scriptId": str(scriptId)},
    }
    return response["bytecode"]


def get_stack_trace(
    stackTraceId: runtime.StackTraceId,
) -> Generator[dict, dict, runtime.StackTrace]:
    """Returns stack trace with given `stackTraceId`.

    Parameters
    ----------
    stackTraceId: runtime.StackTraceId

    Returns
    -------
    stackTrace: runtime.StackTrace

    **Experimental**
    """
    response = yield {
        "method": "Debugger.getStackTrace",
        "params": {"stackTraceId": stackTraceId.to_json()},
    }
    return runtime.StackTrace.from_json(response["stackTrace"])


def pause() -> dict:
    """Stops on the next JavaScript statement."""
    return {"method": "Debugger.pause", "params": {}}


@deprecated(version=1.3)
def pause_on_async_call(parentStackTraceId: runtime.StackTraceId) -> dict:
    """
    Parameters
    ----------
    parentStackTraceId: runtime.StackTraceId
            Debugger will pause when async call with given stack trace is started.

    **Experimental**
    """
    return {
        "method": "Debugger.pauseOnAsyncCall",
        "params": {"parentStackTraceId": parentStackTraceId.to_json()},
    }


def remove_breakpoint(breakpointId: BreakpointId) -> dict:
    """Removes JavaScript breakpoint.

    Parameters
    ----------
    breakpointId: BreakpointId
    """
    return {
        "method": "Debugger.removeBreakpoint",
        "params": {"breakpointId": str(breakpointId)},
    }


def restart_frame(callFrameId: CallFrameId) -> Generator[dict, dict, dict]:
    """Restarts particular call frame from the beginning.

    Parameters
    ----------
    callFrameId: CallFrameId
            Call frame identifier to evaluate on.

    Returns
    -------
    callFrames: list[CallFrame]
            New stack trace.
    asyncStackTrace: Optional[runtime.StackTrace]
            Async stack trace, if any.
    asyncStackTraceId: Optional[runtime.StackTraceId]
            Async stack trace, if any.
    """
    response = yield {
        "method": "Debugger.restartFrame",
        "params": {"callFrameId": str(callFrameId)},
    }
    return {
        "callFrames": [CallFrame.from_json(c) for c in response["callFrames"]],
        "asyncStackTrace": runtime.StackTrace.from_json(response["asyncStackTrace"])
        if "asyncStackTrace" in response
        else None,
        "asyncStackTraceId": runtime.StackTraceId.from_json(
            response["asyncStackTraceId"]
        )
        if "asyncStackTraceId" in response
        else None,
    }


def resume(terminateOnResume: Optional[bool] = None) -> dict:
    """Resumes JavaScript execution.

    Parameters
    ----------
    terminateOnResume: Optional[bool]
            Set to true to terminate execution upon resuming execution. In contrast
            to Runtime.terminateExecution, this will allows to execute further
            JavaScript (i.e. via evaluation) until execution of the paused code
            is actually resumed, at which point termination is triggered.
            If execution is currently not paused, this parameter has no effect.
    """
    return {
        "method": "Debugger.resume",
        "params": filter_none({"terminateOnResume": terminateOnResume}),
    }


def search_in_content(
    scriptId: runtime.ScriptId,
    query: str,
    caseSensitive: Optional[bool] = None,
    isRegex: Optional[bool] = None,
) -> Generator[dict, dict, list[SearchMatch]]:
    """Searches for given string in script content.

    Parameters
    ----------
    scriptId: runtime.ScriptId
            Id of the script to search in.
    query: str
            String to search for.
    caseSensitive: Optional[bool]
            If true, search is case sensitive.
    isRegex: Optional[bool]
            If true, treats string parameter as regex.

    Returns
    -------
    result: list[SearchMatch]
            List of search matches.
    """
    response = yield {
        "method": "Debugger.searchInContent",
        "params": filter_none(
            {
                "scriptId": str(scriptId),
                "query": query,
                "caseSensitive": caseSensitive,
                "isRegex": isRegex,
            }
        ),
    }
    return [SearchMatch.from_json(r) for r in response["result"]]


def set_async_call_stack_depth(maxDepth: int) -> dict:
    """Enables or disables async call stacks tracking.

    Parameters
    ----------
    maxDepth: int
            Maximum depth of async call stacks. Setting to `0` will effectively disable collecting async
            call stacks (default).
    """
    return {
        "method": "Debugger.setAsyncCallStackDepth",
        "params": {"maxDepth": maxDepth},
    }


def set_blackbox_patterns(patterns: list[str]) -> dict:
    """Replace previous blackbox patterns with passed ones. Forces backend to skip stepping/pausing in
    scripts with url matching one of the patterns. VM will try to leave blackboxed script by
    performing 'step in' several times, finally resorting to 'step out' if unsuccessful.

    Parameters
    ----------
    patterns: list[str]
            Array of regexps that will be used to check script url for blackbox state.

    **Experimental**
    """
    return {"method": "Debugger.setBlackboxPatterns", "params": {"patterns": patterns}}


def set_blackboxed_ranges(
    scriptId: runtime.ScriptId, positions: list[ScriptPosition]
) -> dict:
    """Makes backend skip steps in the script in blackboxed ranges. VM will try leave blacklisted
    scripts by performing 'step in' several times, finally resorting to 'step out' if unsuccessful.
    Positions array contains positions where blackbox state is changed. First interval isn't
    blackboxed. Array should be sorted.

    Parameters
    ----------
    scriptId: runtime.ScriptId
            Id of the script.
    positions: list[ScriptPosition]

    **Experimental**
    """
    return {
        "method": "Debugger.setBlackboxedRanges",
        "params": {
            "scriptId": str(scriptId),
            "positions": [p.to_json() for p in positions],
        },
    }


def set_breakpoint(
    location: Location, condition: Optional[str] = None
) -> Generator[dict, dict, dict]:
    """Sets JavaScript breakpoint at a given location.

    Parameters
    ----------
    location: Location
            Location to set breakpoint in.
    condition: Optional[str]
            Expression to use as a breakpoint condition. When specified, debugger will only stop on the
            breakpoint if this expression evaluates to true.

    Returns
    -------
    breakpointId: BreakpointId
            Id of the created breakpoint for further reference.
    actualLocation: Location
            Location this breakpoint resolved into.
    """
    response = yield {
        "method": "Debugger.setBreakpoint",
        "params": filter_none({"location": location.to_json(), "condition": condition}),
    }
    return {
        "breakpointId": BreakpointId(response["breakpointId"]),
        "actualLocation": Location.from_json(response["actualLocation"]),
    }


def set_instrumentation_breakpoint(
    instrumentation: str,
) -> Generator[dict, dict, BreakpointId]:
    """Sets instrumentation breakpoint.

    Parameters
    ----------
    instrumentation: str
            Instrumentation name.

    Returns
    -------
    breakpointId: BreakpointId
            Id of the created breakpoint for further reference.
    """
    response = yield {
        "method": "Debugger.setInstrumentationBreakpoint",
        "params": {"instrumentation": instrumentation},
    }
    return BreakpointId(response["breakpointId"])


def set_breakpoint_by_url(
    lineNumber: int,
    url: Optional[str] = None,
    urlRegex: Optional[str] = None,
    scriptHash: Optional[str] = None,
    columnNumber: Optional[int] = None,
    condition: Optional[str] = None,
) -> Generator[dict, dict, dict]:
    """Sets JavaScript breakpoint at given location specified either by URL or URL regex. Once this
    command is issued, all existing parsed scripts will have breakpoints resolved and returned in
    `locations` property. Further matching script parsing will result in subsequent
    `breakpointResolved` events issued. This logical breakpoint will survive page reloads.

    Parameters
    ----------
    lineNumber: int
            Line number to set breakpoint at.
    url: Optional[str]
            URL of the resources to set breakpoint on.
    urlRegex: Optional[str]
            Regex pattern for the URLs of the resources to set breakpoints on. Either `url` or
            `urlRegex` must be specified.
    scriptHash: Optional[str]
            Script hash of the resources to set breakpoint on.
    columnNumber: Optional[int]
            Offset in the line to set breakpoint at.
    condition: Optional[str]
            Expression to use as a breakpoint condition. When specified, debugger will only stop on the
            breakpoint if this expression evaluates to true.

    Returns
    -------
    breakpointId: BreakpointId
            Id of the created breakpoint for further reference.
    locations: list[Location]
            List of the locations this breakpoint resolved into upon addition.
    """
    response = yield {
        "method": "Debugger.setBreakpointByUrl",
        "params": filter_none(
            {
                "lineNumber": lineNumber,
                "url": url,
                "urlRegex": urlRegex,
                "scriptHash": scriptHash,
                "columnNumber": columnNumber,
                "condition": condition,
            }
        ),
    }
    return {
        "breakpointId": BreakpointId(response["breakpointId"]),
        "locations": [Location.from_json(l) for l in response["locations"]],
    }


def set_breakpoint_on_function_call(
    objectId: runtime.RemoteObjectId, condition: Optional[str] = None
) -> Generator[dict, dict, BreakpointId]:
    """Sets JavaScript breakpoint before each call to the given function.
    If another function was created from the same source as a given one,
    calling it will also trigger the breakpoint.

    Parameters
    ----------
    objectId: runtime.RemoteObjectId
            Function object id.
    condition: Optional[str]
            Expression to use as a breakpoint condition. When specified, debugger will
            stop on the breakpoint if this expression evaluates to true.

    Returns
    -------
    breakpointId: BreakpointId
            Id of the created breakpoint for further reference.

    **Experimental**
    """
    response = yield {
        "method": "Debugger.setBreakpointOnFunctionCall",
        "params": filter_none({"objectId": str(objectId), "condition": condition}),
    }
    return BreakpointId(response["breakpointId"])


def set_breakpoints_active(active: bool) -> dict:
    """Activates / deactivates all breakpoints on the page.

    Parameters
    ----------
    active: bool
            New value for breakpoints active state.
    """
    return {"method": "Debugger.setBreakpointsActive", "params": {"active": active}}


def set_pause_on_exceptions(state: str) -> dict:
    """Defines pause on exceptions state. Can be set to stop on all exceptions, uncaught exceptions or
    no exceptions. Initial pause on exceptions state is `none`.

    Parameters
    ----------
    state: str
            Pause on exceptions mode.
    """
    return {"method": "Debugger.setPauseOnExceptions", "params": {"state": state}}


def set_return_value(newValue: runtime.CallArgument) -> dict:
    """Changes return value in top frame. Available only at return break position.

    Parameters
    ----------
    newValue: runtime.CallArgument
            New return value.

    **Experimental**
    """
    return {
        "method": "Debugger.setReturnValue",
        "params": {"newValue": newValue.to_json()},
    }


def set_script_source(
    scriptId: runtime.ScriptId, scriptSource: str, dryRun: Optional[bool] = None
) -> Generator[dict, dict, dict]:
    """Edits JavaScript source live.

    Parameters
    ----------
    scriptId: runtime.ScriptId
            Id of the script to edit.
    scriptSource: str
            New content of the script.
    dryRun: Optional[bool]
            If true the change will not actually be applied. Dry run may be used to get result
            description without actually modifying the code.

    Returns
    -------
    callFrames: Optional[list[CallFrame]]
            New stack trace in case editing has happened while VM was stopped.
    stackChanged: Optional[bool]
            Whether current call stack  was modified after applying the changes.
    asyncStackTrace: Optional[runtime.StackTrace]
            Async stack trace, if any.
    asyncStackTraceId: Optional[runtime.StackTraceId]
            Async stack trace, if any.
    exceptionDetails: Optional[runtime.ExceptionDetails]
            Exception details if any.
    """
    response = yield {
        "method": "Debugger.setScriptSource",
        "params": filter_none(
            {"scriptId": str(scriptId), "scriptSource": scriptSource, "dryRun": dryRun}
        ),
    }
    return {
        "callFrames": [CallFrame.from_json(c) for c in response["callFrames"]]
        if "callFrames" in response
        else None,
        "stackChanged": response.get("stackChanged"),
        "asyncStackTrace": runtime.StackTrace.from_json(response["asyncStackTrace"])
        if "asyncStackTrace" in response
        else None,
        "asyncStackTraceId": runtime.StackTraceId.from_json(
            response["asyncStackTraceId"]
        )
        if "asyncStackTraceId" in response
        else None,
        "exceptionDetails": runtime.ExceptionDetails.from_json(
            response["exceptionDetails"]
        )
        if "exceptionDetails" in response
        else None,
    }


def set_skip_all_pauses(skip: bool) -> dict:
    """Makes page not interrupt on any pauses (breakpoint, exception, dom exception etc).

    Parameters
    ----------
    skip: bool
            New value for skip pauses state.
    """
    return {"method": "Debugger.setSkipAllPauses", "params": {"skip": skip}}


def set_variable_value(
    scopeNumber: int,
    variableName: str,
    newValue: runtime.CallArgument,
    callFrameId: CallFrameId,
) -> dict:
    """Changes value of variable in a callframe. Object-based scopes are not supported and must be
    mutated manually.

    Parameters
    ----------
    scopeNumber: int
            0-based number of scope as was listed in scope chain. Only 'local', 'closure' and 'catch'
            scope types are allowed. Other scopes could be manipulated manually.
    variableName: str
            Variable name.
    newValue: runtime.CallArgument
            New variable value.
    callFrameId: CallFrameId
            Id of callframe that holds variable.
    """
    return {
        "method": "Debugger.setVariableValue",
        "params": {
            "scopeNumber": scopeNumber,
            "variableName": variableName,
            "newValue": newValue.to_json(),
            "callFrameId": str(callFrameId),
        },
    }


def step_into(
    breakOnAsyncCall: Optional[bool] = None,
    skipList: Optional[list[LocationRange]] = None,
) -> dict:
    """Steps into the function call.

    Parameters
    ----------
    breakOnAsyncCall: Optional[bool]
            Debugger will pause on the execution of the first async task which was scheduled
            before next pause.
    skipList: Optional[list[LocationRange]]
            The skipList specifies location ranges that should be skipped on step into.
    """
    return {
        "method": "Debugger.stepInto",
        "params": filter_none(
            {
                "breakOnAsyncCall": breakOnAsyncCall,
                "skipList": [s.to_json() for s in skipList] if skipList else None,
            }
        ),
    }


def step_out() -> dict:
    """Steps out of the function call."""
    return {"method": "Debugger.stepOut", "params": {}}


def step_over(skipList: Optional[list[LocationRange]] = None) -> dict:
    """Steps over the statement.

    Parameters
    ----------
    skipList: Optional[list[LocationRange]]
            The skipList specifies location ranges that should be skipped on step over.
    """
    return {
        "method": "Debugger.stepOver",
        "params": filter_none(
            {"skipList": [s.to_json() for s in skipList] if skipList else None}
        ),
    }


@dataclasses.dataclass
class BreakpointResolved:
    """Fired when breakpoint is resolved to an actual script and location.

    Attributes
    ----------
    breakpointId: BreakpointId
            Breakpoint unique identifier.
    location: Location
            Actual breakpoint location.
    """

    breakpointId: BreakpointId
    location: Location

    @classmethod
    def from_json(cls, json: dict) -> BreakpointResolved:
        return cls(
            BreakpointId(json["breakpointId"]), Location.from_json(json["location"])
        )


@dataclasses.dataclass
class Paused:
    """Fired when the virtual machine stopped on breakpoint or exception or any other stop criteria.

    Attributes
    ----------
    callFrames: list[CallFrame]
            Call stack the virtual machine stopped on.
    reason: str
            Pause reason.
    data: Optional[dict]
            Object containing break-specific auxiliary properties.
    hitBreakpoints: Optional[list[str]]
            Hit breakpoints IDs
    asyncStackTrace: Optional[runtime.StackTrace]
            Async stack trace, if any.
    asyncStackTraceId: Optional[runtime.StackTraceId]
            Async stack trace, if any.
    asyncCallStackTraceId: Optional[runtime.StackTraceId]
            Never present, will be removed.
    """

    callFrames: list[CallFrame]
    reason: str
    data: Optional[dict] = None
    hitBreakpoints: Optional[list[str]] = None
    asyncStackTrace: Optional[runtime.StackTrace] = None
    asyncStackTraceId: Optional[runtime.StackTraceId] = None
    asyncCallStackTraceId: Optional[runtime.StackTraceId] = None

    @classmethod
    def from_json(cls, json: dict) -> Paused:
        return cls(
            [CallFrame.from_json(c) for c in json["callFrames"]],
            json["reason"],
            json.get("data"),
            json.get("hitBreakpoints"),
            runtime.StackTrace.from_json(json["asyncStackTrace"])
            if "asyncStackTrace" in json
            else None,
            runtime.StackTraceId.from_json(json["asyncStackTraceId"])
            if "asyncStackTraceId" in json
            else None,
            runtime.StackTraceId.from_json(json["asyncCallStackTraceId"])
            if "asyncCallStackTraceId" in json
            else None,
        )


@dataclasses.dataclass
class Resumed:
    """Fired when the virtual machine resumed execution."""

    @classmethod
    def from_json(cls, json: dict) -> Resumed:
        return cls()


@dataclasses.dataclass
class ScriptFailedToParse:
    """Fired when virtual machine fails to parse the script.

    Attributes
    ----------
    scriptId: runtime.ScriptId
            Identifier of the script parsed.
    url: str
            URL or name of the script parsed (if any).
    startLine: int
            Line offset of the script within the resource with given URL (for script tags).
    startColumn: int
            Column offset of the script within the resource with given URL.
    endLine: int
            Last line of the script.
    endColumn: int
            Length of the last line of the script.
    executionContextId: runtime.ExecutionContextId
            Specifies script creation context.
    hash: str
            Content hash of the script.
    executionContextAuxData: Optional[dict]
            Embedder-specific auxiliary data.
    sourceMapURL: Optional[str]
            URL of source map associated with script (if any).
    hasSourceURL: Optional[bool]
            True, if this script has sourceURL.
    isModule: Optional[bool]
            True, if this script is ES6 module.
    length: Optional[int]
            This script length.
    stackTrace: Optional[runtime.StackTrace]
            JavaScript top stack frame of where the script parsed event was triggered if available.
    codeOffset: Optional[int]
            If the scriptLanguage is WebAssembly, the code section offset in the module.
    scriptLanguage: Optional[ScriptLanguage]
            The language of the script.
    embedderName: Optional[str]
            The name the embedder supplied for this script.
    """

    scriptId: runtime.ScriptId
    url: str
    startLine: int
    startColumn: int
    endLine: int
    endColumn: int
    executionContextId: runtime.ExecutionContextId
    hash: str
    executionContextAuxData: Optional[dict] = None
    sourceMapURL: Optional[str] = None
    hasSourceURL: Optional[bool] = None
    isModule: Optional[bool] = None
    length: Optional[int] = None
    stackTrace: Optional[runtime.StackTrace] = None
    codeOffset: Optional[int] = None
    scriptLanguage: Optional[ScriptLanguage] = None
    embedderName: Optional[str] = None

    @classmethod
    def from_json(cls, json: dict) -> ScriptFailedToParse:
        return cls(
            runtime.ScriptId(json["scriptId"]),
            json["url"],
            json["startLine"],
            json["startColumn"],
            json["endLine"],
            json["endColumn"],
            runtime.ExecutionContextId(json["executionContextId"]),
            json["hash"],
            json.get("executionContextAuxData"),
            json.get("sourceMapURL"),
            json.get("hasSourceURL"),
            json.get("isModule"),
            json.get("length"),
            runtime.StackTrace.from_json(json["stackTrace"])
            if "stackTrace" in json
            else None,
            json.get("codeOffset"),
            ScriptLanguage(json["scriptLanguage"])
            if "scriptLanguage" in json
            else None,
            json.get("embedderName"),
        )


@dataclasses.dataclass
class ScriptParsed:
    """Fired when virtual machine parses script. This event is also fired for all known and uncollected
    scripts upon enabling debugger.

    Attributes
    ----------
    scriptId: runtime.ScriptId
            Identifier of the script parsed.
    url: str
            URL or name of the script parsed (if any).
    startLine: int
            Line offset of the script within the resource with given URL (for script tags).
    startColumn: int
            Column offset of the script within the resource with given URL.
    endLine: int
            Last line of the script.
    endColumn: int
            Length of the last line of the script.
    executionContextId: runtime.ExecutionContextId
            Specifies script creation context.
    hash: str
            Content hash of the script.
    executionContextAuxData: Optional[dict]
            Embedder-specific auxiliary data.
    isLiveEdit: Optional[bool]
            True, if this script is generated as a result of the live edit operation.
    sourceMapURL: Optional[str]
            URL of source map associated with script (if any).
    hasSourceURL: Optional[bool]
            True, if this script has sourceURL.
    isModule: Optional[bool]
            True, if this script is ES6 module.
    length: Optional[int]
            This script length.
    stackTrace: Optional[runtime.StackTrace]
            JavaScript top stack frame of where the script parsed event was triggered if available.
    codeOffset: Optional[int]
            If the scriptLanguage is WebAssembly, the code section offset in the module.
    scriptLanguage: Optional[ScriptLanguage]
            The language of the script.
    debugSymbols: Optional[DebugSymbols]
            If the scriptLanguage is WebASsembly, the source of debug symbols for the module.
    embedderName: Optional[str]
            The name the embedder supplied for this script.
    """

    scriptId: runtime.ScriptId
    url: str
    startLine: int
    startColumn: int
    endLine: int
    endColumn: int
    executionContextId: runtime.ExecutionContextId
    hash: str
    executionContextAuxData: Optional[dict] = None
    isLiveEdit: Optional[bool] = None
    sourceMapURL: Optional[str] = None
    hasSourceURL: Optional[bool] = None
    isModule: Optional[bool] = None
    length: Optional[int] = None
    stackTrace: Optional[runtime.StackTrace] = None
    codeOffset: Optional[int] = None
    scriptLanguage: Optional[ScriptLanguage] = None
    debugSymbols: Optional[DebugSymbols] = None
    embedderName: Optional[str] = None

    @classmethod
    def from_json(cls, json: dict) -> ScriptParsed:
        return cls(
            runtime.ScriptId(json["scriptId"]),
            json["url"],
            json["startLine"],
            json["startColumn"],
            json["endLine"],
            json["endColumn"],
            runtime.ExecutionContextId(json["executionContextId"]),
            json["hash"],
            json.get("executionContextAuxData"),
            json.get("isLiveEdit"),
            json.get("sourceMapURL"),
            json.get("hasSourceURL"),
            json.get("isModule"),
            json.get("length"),
            runtime.StackTrace.from_json(json["stackTrace"])
            if "stackTrace" in json
            else None,
            json.get("codeOffset"),
            ScriptLanguage(json["scriptLanguage"])
            if "scriptLanguage" in json
            else None,
            DebugSymbols.from_json(json["debugSymbols"])
            if "debugSymbols" in json
            else None,
            json.get("embedderName"),
        )
