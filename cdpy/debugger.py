from __future__ import annotations

import dataclasses
import enum
from typing import Optional

from . import runtime
from .common import filter_none, filter_unset_parameters


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
            [Scope.from_json(x) for x in json["scopeChain"]],
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


def continue_to_location(location: Location, targetCallFrames: Optional[str] = None):
    """Continues execution until specific location is reached.

    Parameters
    ----------
    location: Location
            Location to continue to.
    targetCallFrames: Optional[str]
    """
    return filter_unset_parameters(
        {
            "method": "Debugger.continueToLocation",
            "params": {"location": location, "targetCallFrames": targetCallFrames},
        }
    )


def disable():
    """Disables debugger for given page."""
    return {"method": "Debugger.disable", "params": {}}


def enable(maxScriptsCacheSize: Optional[float] = None):
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
    return filter_unset_parameters(
        {
            "method": "Debugger.enable",
            "params": {"maxScriptsCacheSize": maxScriptsCacheSize},
        }
    )


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
):
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
    return filter_unset_parameters(
        {
            "method": "Debugger.evaluateOnCallFrame",
            "params": {
                "callFrameId": callFrameId,
                "expression": expression,
                "objectGroup": objectGroup,
                "includeCommandLineAPI": includeCommandLineAPI,
                "silent": silent,
                "returnByValue": returnByValue,
                "generatePreview": generatePreview,
                "throwOnSideEffect": throwOnSideEffect,
                "timeout": timeout,
            },
        }
    )


def execute_wasm_evaluator(
    callFrameId: CallFrameId,
    evaluator: str,
    timeout: Optional[runtime.TimeDelta] = None,
):
    """Execute a Wasm Evaluator module on a given call frame.

    **Experimental**

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
    """
    return filter_unset_parameters(
        {
            "method": "Debugger.executeWasmEvaluator",
            "params": {
                "callFrameId": callFrameId,
                "evaluator": evaluator,
                "timeout": timeout,
            },
        }
    )


def get_possible_breakpoints(
    start: Location,
    end: Optional[Location] = None,
    restrictToFunction: Optional[bool] = None,
):
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
    return filter_unset_parameters(
        {
            "method": "Debugger.getPossibleBreakpoints",
            "params": {
                "start": start,
                "end": end,
                "restrictToFunction": restrictToFunction,
            },
        }
    )


def get_script_source(scriptId: runtime.ScriptId):
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
    return {"method": "Debugger.getScriptSource", "params": {"scriptId": scriptId}}


def get_wasm_bytecode(scriptId: runtime.ScriptId):
    """This command is deprecated. Use getScriptSource instead.

    **Deprectated**

    Parameters
    ----------
    scriptId: runtime.ScriptId
            Id of the Wasm script to get source for.

    Returns
    -------
    bytecode: str
            Script source. (Encoded as a base64 string when passed over JSON)
    """
    return {"method": "Debugger.getWasmBytecode", "params": {"scriptId": scriptId}}


def get_stack_trace(stackTraceId: runtime.StackTraceId):
    """Returns stack trace with given `stackTraceId`.

    **Experimental**

    Parameters
    ----------
    stackTraceId: runtime.StackTraceId

    Returns
    -------
    stackTrace: runtime.StackTrace
    """
    return {
        "method": "Debugger.getStackTrace",
        "params": {"stackTraceId": stackTraceId},
    }


def pause():
    """Stops on the next JavaScript statement."""
    return {"method": "Debugger.pause", "params": {}}


def pause_on_async_call(parentStackTraceId: runtime.StackTraceId):
    """
    **Experimental**

    **Deprectated**

    Parameters
    ----------
    parentStackTraceId: runtime.StackTraceId
            Debugger will pause when async call with given stack trace is started.
    """
    return {
        "method": "Debugger.pauseOnAsyncCall",
        "params": {"parentStackTraceId": parentStackTraceId},
    }


def remove_breakpoint(breakpointId: BreakpointId):
    """Removes JavaScript breakpoint.

    Parameters
    ----------
    breakpointId: BreakpointId
    """
    return {
        "method": "Debugger.removeBreakpoint",
        "params": {"breakpointId": breakpointId},
    }


def restart_frame(callFrameId: CallFrameId):
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
    return {"method": "Debugger.restartFrame", "params": {"callFrameId": callFrameId}}


def resume(terminateOnResume: Optional[bool] = None):
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
    return filter_unset_parameters(
        {
            "method": "Debugger.resume",
            "params": {"terminateOnResume": terminateOnResume},
        }
    )


def search_in_content(
    scriptId: runtime.ScriptId,
    query: str,
    caseSensitive: Optional[bool] = None,
    isRegex: Optional[bool] = None,
):
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
    return filter_unset_parameters(
        {
            "method": "Debugger.searchInContent",
            "params": {
                "scriptId": scriptId,
                "query": query,
                "caseSensitive": caseSensitive,
                "isRegex": isRegex,
            },
        }
    )


def set_async_call_stack_depth(maxDepth: int):
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


def set_blackbox_patterns(patterns: list[str]):
    """Replace previous blackbox patterns with passed ones. Forces backend to skip stepping/pausing in
    scripts with url matching one of the patterns. VM will try to leave blackboxed script by
    performing 'step in' several times, finally resorting to 'step out' if unsuccessful.

    **Experimental**

    Parameters
    ----------
    patterns: list[str]
            Array of regexps that will be used to check script url for blackbox state.
    """
    return {"method": "Debugger.setBlackboxPatterns", "params": {"patterns": patterns}}


def set_blackboxed_ranges(scriptId: runtime.ScriptId, positions: list[ScriptPosition]):
    """Makes backend skip steps in the script in blackboxed ranges. VM will try leave blacklisted
    scripts by performing 'step in' several times, finally resorting to 'step out' if unsuccessful.
    Positions array contains positions where blackbox state is changed. First interval isn't
    blackboxed. Array should be sorted.

    **Experimental**

    Parameters
    ----------
    scriptId: runtime.ScriptId
            Id of the script.
    positions: list[ScriptPosition]
    """
    return {
        "method": "Debugger.setBlackboxedRanges",
        "params": {"scriptId": scriptId, "positions": positions},
    }


def set_breakpoint(location: Location, condition: Optional[str] = None):
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
    return filter_unset_parameters(
        {
            "method": "Debugger.setBreakpoint",
            "params": {"location": location, "condition": condition},
        }
    )


def set_instrumentation_breakpoint(instrumentation: str):
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
    return {
        "method": "Debugger.setInstrumentationBreakpoint",
        "params": {"instrumentation": instrumentation},
    }


def set_breakpoint_by_url(
    lineNumber: int,
    url: Optional[str] = None,
    urlRegex: Optional[str] = None,
    scriptHash: Optional[str] = None,
    columnNumber: Optional[int] = None,
    condition: Optional[str] = None,
):
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
    return filter_unset_parameters(
        {
            "method": "Debugger.setBreakpointByUrl",
            "params": {
                "lineNumber": lineNumber,
                "url": url,
                "urlRegex": urlRegex,
                "scriptHash": scriptHash,
                "columnNumber": columnNumber,
                "condition": condition,
            },
        }
    )


def set_breakpoint_on_function_call(
    objectId: runtime.RemoteObjectId, condition: Optional[str] = None
):
    """Sets JavaScript breakpoint before each call to the given function.
    If another function was created from the same source as a given one,
    calling it will also trigger the breakpoint.

    **Experimental**

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
    """
    return filter_unset_parameters(
        {
            "method": "Debugger.setBreakpointOnFunctionCall",
            "params": {"objectId": objectId, "condition": condition},
        }
    )


def set_breakpoints_active(active: bool):
    """Activates / deactivates all breakpoints on the page.

    Parameters
    ----------
    active: bool
            New value for breakpoints active state.
    """
    return {"method": "Debugger.setBreakpointsActive", "params": {"active": active}}


def set_pause_on_exceptions(state: str):
    """Defines pause on exceptions state. Can be set to stop on all exceptions, uncaught exceptions or
    no exceptions. Initial pause on exceptions state is `none`.

    Parameters
    ----------
    state: str
            Pause on exceptions mode.
    """
    return {"method": "Debugger.setPauseOnExceptions", "params": {"state": state}}


def set_return_value(newValue: runtime.CallArgument):
    """Changes return value in top frame. Available only at return break position.

    **Experimental**

    Parameters
    ----------
    newValue: runtime.CallArgument
            New return value.
    """
    return {"method": "Debugger.setReturnValue", "params": {"newValue": newValue}}


def set_script_source(
    scriptId: runtime.ScriptId, scriptSource: str, dryRun: Optional[bool] = None
):
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
    return filter_unset_parameters(
        {
            "method": "Debugger.setScriptSource",
            "params": {
                "scriptId": scriptId,
                "scriptSource": scriptSource,
                "dryRun": dryRun,
            },
        }
    )


def set_skip_all_pauses(skip: bool):
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
):
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
            "newValue": newValue,
            "callFrameId": callFrameId,
        },
    }


def step_into(
    breakOnAsyncCall: Optional[bool] = None,
    skipList: Optional[list[LocationRange]] = None,
):
    """Steps into the function call.

    Parameters
    ----------
    breakOnAsyncCall: Optional[bool]
            Debugger will pause on the execution of the first async task which was scheduled
            before next pause.
    skipList: Optional[list[LocationRange]]
            The skipList specifies location ranges that should be skipped on step into.
    """
    return filter_unset_parameters(
        {
            "method": "Debugger.stepInto",
            "params": {"breakOnAsyncCall": breakOnAsyncCall, "skipList": skipList},
        }
    )


def step_out():
    """Steps out of the function call."""
    return {"method": "Debugger.stepOut", "params": {}}


def step_over(skipList: Optional[list[LocationRange]] = None):
    """Steps over the statement.

    Parameters
    ----------
    skipList: Optional[list[LocationRange]]
            The skipList specifies location ranges that should be skipped on step over.
    """
    return filter_unset_parameters(
        {"method": "Debugger.stepOver", "params": {"skipList": skipList}}
    )
