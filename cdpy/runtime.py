from __future__ import annotations

import dataclasses
from typing import Generator, Optional

from .common import filter_none, filter_unset_parameters


class ScriptId(str):
    """Unique script identifier."""

    def __repr__(self):
        return f"ScriptId({super().__repr__()})"


class RemoteObjectId(str):
    """Unique object identifier."""

    def __repr__(self):
        return f"RemoteObjectId({super().__repr__()})"


class UnserializableValue(str):
    """Primitive value which cannot be JSON-stringified. Includes values `-0`, `NaN`, `Infinity`,
    `-Infinity`, and bigint literals.
    """

    def __repr__(self):
        return f"UnserializableValue({super().__repr__()})"


@dataclasses.dataclass
class RemoteObject:
    """Mirror object referencing original JavaScript object.

    Attributes
    ----------
    type: str
            Object type.
    subtype: Optional[str]
            Object subtype hint. Specified for `object` or `wasm` type values only.
    className: Optional[str]
            Object class (constructor) name. Specified for `object` type values only.
    value: Optional[any]
            Remote object value in case of primitive values or JSON values (if it was requested).
    unserializableValue: Optional[UnserializableValue]
            Primitive value which can not be JSON-stringified does not have `value`, but gets this
            property.
    description: Optional[str]
            String representation of the object.
    objectId: Optional[RemoteObjectId]
            Unique object identifier (for non-primitive values).
    preview: Optional[ObjectPreview]
            Preview containing abbreviated property values. Specified for `object` type values only.
    customPreview: Optional[CustomPreview]
    """

    type: str
    subtype: Optional[str] = None
    className: Optional[str] = None
    value: Optional[any] = None
    unserializableValue: Optional[UnserializableValue] = None
    description: Optional[str] = None
    objectId: Optional[RemoteObjectId] = None
    preview: Optional[ObjectPreview] = None
    customPreview: Optional[CustomPreview] = None

    @classmethod
    def from_json(cls, json: dict) -> RemoteObject:
        return cls(
            json["type"],
            json.get("subtype"),
            json.get("className"),
            json.get("value"),
            UnserializableValue(json["unserializableValue"])
            if "unserializableValue" in json
            else None,
            json.get("description"),
            RemoteObjectId(json["objectId"]) if "objectId" in json else None,
            ObjectPreview.from_json(json["preview"]) if "preview" in json else None,
            CustomPreview.from_json(json["customPreview"])
            if "customPreview" in json
            else None,
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "type": self.type,
                "subtype": self.subtype,
                "className": self.className,
                "value": self.value,
                "unserializableValue": str(self.unserializableValue)
                if self.unserializableValue
                else None,
                "description": self.description,
                "objectId": str(self.objectId) if self.objectId else None,
                "preview": self.preview.to_json() if self.preview else None,
                "customPreview": self.customPreview.to_json()
                if self.customPreview
                else None,
            }
        )


@dataclasses.dataclass
class CustomPreview:
    """
    Attributes
    ----------
    header: str
            The JSON-stringified result of formatter.header(object, config) call.
            It contains json ML array that represents RemoteObject.
    bodyGetterId: Optional[RemoteObjectId]
            If formatter returns true as a result of formatter.hasBody call then bodyGetterId will
            contain RemoteObjectId for the function that returns result of formatter.body(object, config) call.
            The result value is json ML array.
    """

    header: str
    bodyGetterId: Optional[RemoteObjectId] = None

    @classmethod
    def from_json(cls, json: dict) -> CustomPreview:
        return cls(
            json["header"],
            RemoteObjectId(json["bodyGetterId"]) if "bodyGetterId" in json else None,
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "header": self.header,
                "bodyGetterId": str(self.bodyGetterId) if self.bodyGetterId else None,
            }
        )


@dataclasses.dataclass
class ObjectPreview:
    """Object containing abbreviated remote object value.

    Attributes
    ----------
    type: str
            Object type.
    overflow: bool
            True iff some of the properties or entries of the original object did not fit.
    properties: list[PropertyPreview]
            List of the properties.
    subtype: Optional[str]
            Object subtype hint. Specified for `object` type values only.
    description: Optional[str]
            String representation of the object.
    entries: Optional[list[EntryPreview]]
            List of the entries. Specified for `map` and `set` subtype values only.
    """

    type: str
    overflow: bool
    properties: list[PropertyPreview]
    subtype: Optional[str] = None
    description: Optional[str] = None
    entries: Optional[list[EntryPreview]] = None

    @classmethod
    def from_json(cls, json: dict) -> ObjectPreview:
        return cls(
            json["type"],
            json["overflow"],
            [PropertyPreview.from_json(p) for p in json["properties"]],
            json.get("subtype"),
            json.get("description"),
            [EntryPreview.from_json(e) for e in json["entries"]]
            if "entries" in json
            else None,
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "type": self.type,
                "overflow": self.overflow,
                "properties": [p.to_json() for p in self.properties],
                "subtype": self.subtype,
                "description": self.description,
                "entries": [e.to_json() for e in self.entries]
                if self.entries
                else None,
            }
        )


@dataclasses.dataclass
class PropertyPreview:
    """
    Attributes
    ----------
    name: str
            Property name.
    type: str
            Object type. Accessor means that the property itself is an accessor property.
    value: Optional[str]
            User-friendly property value string.
    valuePreview: Optional[ObjectPreview]
            Nested value preview.
    subtype: Optional[str]
            Object subtype hint. Specified for `object` type values only.
    """

    name: str
    type: str
    value: Optional[str] = None
    valuePreview: Optional[ObjectPreview] = None
    subtype: Optional[str] = None

    @classmethod
    def from_json(cls, json: dict) -> PropertyPreview:
        return cls(
            json["name"],
            json["type"],
            json.get("value"),
            ObjectPreview.from_json(json["valuePreview"])
            if "valuePreview" in json
            else None,
            json.get("subtype"),
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "name": self.name,
                "type": self.type,
                "value": self.value,
                "valuePreview": self.valuePreview.to_json()
                if self.valuePreview
                else None,
                "subtype": self.subtype,
            }
        )


@dataclasses.dataclass
class EntryPreview:
    """
    Attributes
    ----------
    value: ObjectPreview
            Preview of the value.
    key: Optional[ObjectPreview]
            Preview of the key. Specified for map-like collection entries.
    """

    value: ObjectPreview
    key: Optional[ObjectPreview] = None

    @classmethod
    def from_json(cls, json: dict) -> EntryPreview:
        return cls(
            ObjectPreview.from_json(json["value"]),
            ObjectPreview.from_json(json["key"]) if "key" in json else None,
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "value": self.value.to_json(),
                "key": self.key.to_json() if self.key else None,
            }
        )


@dataclasses.dataclass
class PropertyDescriptor:
    """Object property descriptor.

    Attributes
    ----------
    name: str
            Property name or symbol description.
    configurable: bool
            True if the type of this property descriptor may be changed and if the property may be
            deleted from the corresponding object.
    enumerable: bool
            True if this property shows up during enumeration of the properties on the corresponding
            object.
    value: Optional[RemoteObject]
            The value associated with the property.
    writable: Optional[bool]
            True if the value associated with the property may be changed (data descriptors only).
    get: Optional[RemoteObject]
            A function which serves as a getter for the property, or `undefined` if there is no getter
            (accessor descriptors only).
    set: Optional[RemoteObject]
            A function which serves as a setter for the property, or `undefined` if there is no setter
            (accessor descriptors only).
    wasThrown: Optional[bool]
            True if the result was thrown during the evaluation.
    isOwn: Optional[bool]
            True if the property is owned for the object.
    symbol: Optional[RemoteObject]
            Property symbol object, if the property is of the `symbol` type.
    """

    name: str
    configurable: bool
    enumerable: bool
    value: Optional[RemoteObject] = None
    writable: Optional[bool] = None
    get: Optional[RemoteObject] = None
    set: Optional[RemoteObject] = None
    wasThrown: Optional[bool] = None
    isOwn: Optional[bool] = None
    symbol: Optional[RemoteObject] = None

    @classmethod
    def from_json(cls, json: dict) -> PropertyDescriptor:
        return cls(
            json["name"],
            json["configurable"],
            json["enumerable"],
            RemoteObject.from_json(json["value"]) if "value" in json else None,
            json.get("writable"),
            RemoteObject.from_json(json["get"]) if "get" in json else None,
            RemoteObject.from_json(json["set"]) if "set" in json else None,
            json.get("wasThrown"),
            json.get("isOwn"),
            RemoteObject.from_json(json["symbol"]) if "symbol" in json else None,
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "name": self.name,
                "configurable": self.configurable,
                "enumerable": self.enumerable,
                "value": self.value.to_json() if self.value else None,
                "writable": self.writable,
                "get": self.get.to_json() if self.get else None,
                "set": self.set.to_json() if self.set else None,
                "wasThrown": self.wasThrown,
                "isOwn": self.isOwn,
                "symbol": self.symbol.to_json() if self.symbol else None,
            }
        )


@dataclasses.dataclass
class InternalPropertyDescriptor:
    """Object internal property descriptor. This property isn't normally visible in JavaScript code.

    Attributes
    ----------
    name: str
            Conventional property name.
    value: Optional[RemoteObject]
            The value associated with the property.
    """

    name: str
    value: Optional[RemoteObject] = None

    @classmethod
    def from_json(cls, json: dict) -> InternalPropertyDescriptor:
        return cls(
            json["name"],
            RemoteObject.from_json(json["value"]) if "value" in json else None,
        )

    def to_json(self) -> dict:
        return filter_none(
            {"name": self.name, "value": self.value.to_json() if self.value else None}
        )


@dataclasses.dataclass
class PrivatePropertyDescriptor:
    """Object private field descriptor.

    Attributes
    ----------
    name: str
            Private property name.
    value: Optional[RemoteObject]
            The value associated with the private property.
    get: Optional[RemoteObject]
            A function which serves as a getter for the private property,
            or `undefined` if there is no getter (accessor descriptors only).
    set: Optional[RemoteObject]
            A function which serves as a setter for the private property,
            or `undefined` if there is no setter (accessor descriptors only).
    """

    name: str
    value: Optional[RemoteObject] = None
    get: Optional[RemoteObject] = None
    set: Optional[RemoteObject] = None

    @classmethod
    def from_json(cls, json: dict) -> PrivatePropertyDescriptor:
        return cls(
            json["name"],
            RemoteObject.from_json(json["value"]) if "value" in json else None,
            RemoteObject.from_json(json["get"]) if "get" in json else None,
            RemoteObject.from_json(json["set"]) if "set" in json else None,
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "name": self.name,
                "value": self.value.to_json() if self.value else None,
                "get": self.get.to_json() if self.get else None,
                "set": self.set.to_json() if self.set else None,
            }
        )


@dataclasses.dataclass
class CallArgument:
    """Represents function call argument. Either remote object id `objectId`, primitive `value`,
    unserializable primitive value or neither of (for undefined) them should be specified.

    Attributes
    ----------
    value: Optional[any]
            Primitive value or serializable javascript object.
    unserializableValue: Optional[UnserializableValue]
            Primitive value which can not be JSON-stringified.
    objectId: Optional[RemoteObjectId]
            Remote object handle.
    """

    value: Optional[any] = None
    unserializableValue: Optional[UnserializableValue] = None
    objectId: Optional[RemoteObjectId] = None

    @classmethod
    def from_json(cls, json: dict) -> CallArgument:
        return cls(
            json.get("value"),
            UnserializableValue(json["unserializableValue"])
            if "unserializableValue" in json
            else None,
            RemoteObjectId(json["objectId"]) if "objectId" in json else None,
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "value": self.value,
                "unserializableValue": str(self.unserializableValue)
                if self.unserializableValue
                else None,
                "objectId": str(self.objectId) if self.objectId else None,
            }
        )


class ExecutionContextId(int):
    """Id of an execution context."""

    def __repr__(self):
        return f"ExecutionContextId({super().__repr__()})"


@dataclasses.dataclass
class ExecutionContextDescription:
    """Description of an isolated world.

    Attributes
    ----------
    id: ExecutionContextId
            Unique id of the execution context. It can be used to specify in which execution context
            script evaluation should be performed.
    origin: str
            Execution context origin.
    name: str
            Human readable name describing given context.
    auxData: Optional[dict]
            Embedder-specific auxiliary data.
    """

    id: ExecutionContextId
    origin: str
    name: str
    auxData: Optional[dict] = None

    @classmethod
    def from_json(cls, json: dict) -> ExecutionContextDescription:
        return cls(
            ExecutionContextId(json["id"]),
            json["origin"],
            json["name"],
            json.get("auxData"),
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "id": int(self.id),
                "origin": self.origin,
                "name": self.name,
                "auxData": self.auxData,
            }
        )


@dataclasses.dataclass
class ExceptionDetails:
    """Detailed information about exception (or error) that was thrown during script compilation or
    execution.

    Attributes
    ----------
    exceptionId: int
            Exception id.
    text: str
            Exception text, which should be used together with exception object when available.
    lineNumber: int
            Line number of the exception location (0-based).
    columnNumber: int
            Column number of the exception location (0-based).
    scriptId: Optional[ScriptId]
            Script ID of the exception location.
    url: Optional[str]
            URL of the exception location, to be used when the script was not reported.
    stackTrace: Optional[StackTrace]
            JavaScript stack trace if available.
    exception: Optional[RemoteObject]
            Exception object if available.
    executionContextId: Optional[ExecutionContextId]
            Identifier of the context where exception happened.
    """

    exceptionId: int
    text: str
    lineNumber: int
    columnNumber: int
    scriptId: Optional[ScriptId] = None
    url: Optional[str] = None
    stackTrace: Optional[StackTrace] = None
    exception: Optional[RemoteObject] = None
    executionContextId: Optional[ExecutionContextId] = None

    @classmethod
    def from_json(cls, json: dict) -> ExceptionDetails:
        return cls(
            json["exceptionId"],
            json["text"],
            json["lineNumber"],
            json["columnNumber"],
            ScriptId(json["scriptId"]) if "scriptId" in json else None,
            json.get("url"),
            StackTrace.from_json(json["stackTrace"]) if "stackTrace" in json else None,
            RemoteObject.from_json(json["exception"]) if "exception" in json else None,
            ExecutionContextId(json["executionContextId"])
            if "executionContextId" in json
            else None,
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "exceptionId": self.exceptionId,
                "text": self.text,
                "lineNumber": self.lineNumber,
                "columnNumber": self.columnNumber,
                "scriptId": str(self.scriptId) if self.scriptId else None,
                "url": self.url,
                "stackTrace": self.stackTrace.to_json() if self.stackTrace else None,
                "exception": self.exception.to_json() if self.exception else None,
                "executionContextId": int(self.executionContextId)
                if self.executionContextId
                else None,
            }
        )


class Timestamp(float):
    """Number of milliseconds since epoch."""

    def __repr__(self):
        return f"Timestamp({super().__repr__()})"


class TimeDelta(float):
    """Number of milliseconds."""

    def __repr__(self):
        return f"TimeDelta({super().__repr__()})"


@dataclasses.dataclass
class CallFrame:
    """Stack entry for runtime errors and assertions.

    Attributes
    ----------
    functionName: str
            JavaScript function name.
    scriptId: ScriptId
            JavaScript script id.
    url: str
            JavaScript script name or url.
    lineNumber: int
            JavaScript script line number (0-based).
    columnNumber: int
            JavaScript script column number (0-based).
    """

    functionName: str
    scriptId: ScriptId
    url: str
    lineNumber: int
    columnNumber: int

    @classmethod
    def from_json(cls, json: dict) -> CallFrame:
        return cls(
            json["functionName"],
            ScriptId(json["scriptId"]),
            json["url"],
            json["lineNumber"],
            json["columnNumber"],
        )

    def to_json(self) -> dict:
        return {
            "functionName": self.functionName,
            "scriptId": str(self.scriptId),
            "url": self.url,
            "lineNumber": self.lineNumber,
            "columnNumber": self.columnNumber,
        }


@dataclasses.dataclass
class StackTrace:
    """Call frames for assertions or error messages.

    Attributes
    ----------
    callFrames: list[CallFrame]
            JavaScript function name.
    description: Optional[str]
            String label of this stack trace. For async traces this may be a name of the function that
            initiated the async call.
    parent: Optional[StackTrace]
            Asynchronous JavaScript stack trace that preceded this stack, if available.
    parentId: Optional[StackTraceId]
            Asynchronous JavaScript stack trace that preceded this stack, if available.
    """

    callFrames: list[CallFrame]
    description: Optional[str] = None
    parent: Optional[StackTrace] = None
    parentId: Optional[StackTraceId] = None

    @classmethod
    def from_json(cls, json: dict) -> StackTrace:
        return cls(
            [CallFrame.from_json(c) for c in json["callFrames"]],
            json.get("description"),
            StackTrace.from_json(json["parent"]) if "parent" in json else None,
            StackTraceId.from_json(json["parentId"]) if "parentId" in json else None,
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "callFrames": [c.to_json() for c in self.callFrames],
                "description": self.description,
                "parent": self.parent.to_json() if self.parent else None,
                "parentId": self.parentId.to_json() if self.parentId else None,
            }
        )


class UniqueDebuggerId(str):
    """Unique identifier of current debugger."""

    def __repr__(self):
        return f"UniqueDebuggerId({super().__repr__()})"


@dataclasses.dataclass
class StackTraceId:
    """If `debuggerId` is set stack trace comes from another debugger and can be resolved there. This
    allows to track cross-debugger calls. See `Runtime.StackTrace` and `Debugger.paused` for usages.

    Attributes
    ----------
    id: str
    debuggerId: Optional[UniqueDebuggerId]
    """

    id: str
    debuggerId: Optional[UniqueDebuggerId] = None

    @classmethod
    def from_json(cls, json: dict) -> StackTraceId:
        return cls(
            json["id"],
            UniqueDebuggerId(json["debuggerId"]) if "debuggerId" in json else None,
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "id": self.id,
                "debuggerId": str(self.debuggerId) if self.debuggerId else None,
            }
        )


def await_promise(
    promiseObjectId: RemoteObjectId,
    returnByValue: Optional[bool] = None,
    generatePreview: Optional[bool] = None,
) -> Generator[dict, dict, dict]:
    """Add handler to promise with given promise object id.

    Parameters
    ----------
    promiseObjectId: RemoteObjectId
            Identifier of the promise.
    returnByValue: Optional[bool]
            Whether the result is expected to be a JSON object that should be sent by value.
    generatePreview: Optional[bool]
            Whether preview should be generated for the result.

    Returns
    -------
    result: RemoteObject
            Promise result. Will contain rejected value if promise was rejected.
    exceptionDetails: Optional[ExceptionDetails]
            Exception details if stack strace is available.
    """
    response = yield filter_unset_parameters(
        {
            "method": "Runtime.awaitPromise",
            "params": {
                "promiseObjectId": str(promiseObjectId),
                "returnByValue": returnByValue,
                "generatePreview": generatePreview,
            },
        }
    )
    return {
        "result": RemoteObject.from_json(response["result"]),
        "exceptionDetails": ExceptionDetails.from_json(response["exceptionDetails"])
        if "exceptionDetails" in response
        else None,
    }


def call_function_on(
    functionDeclaration: str,
    objectId: Optional[RemoteObjectId] = None,
    arguments: Optional[list[CallArgument]] = None,
    silent: Optional[bool] = None,
    returnByValue: Optional[bool] = None,
    generatePreview: Optional[bool] = None,
    userGesture: Optional[bool] = None,
    awaitPromise: Optional[bool] = None,
    executionContextId: Optional[ExecutionContextId] = None,
    objectGroup: Optional[str] = None,
) -> Generator[dict, dict, dict]:
    """Calls function with given declaration on the given object. Object group of the result is
    inherited from the target object.

    Parameters
    ----------
    functionDeclaration: str
            Declaration of the function to call.
    objectId: Optional[RemoteObjectId]
            Identifier of the object to call function on. Either objectId or executionContextId should
            be specified.
    arguments: Optional[list[CallArgument]]
            Call arguments. All call arguments must belong to the same JavaScript world as the target
            object.
    silent: Optional[bool]
            In silent mode exceptions thrown during evaluation are not reported and do not pause
            execution. Overrides `setPauseOnException` state.
    returnByValue: Optional[bool]
            Whether the result is expected to be a JSON object which should be sent by value.
    generatePreview: Optional[bool]
            Whether preview should be generated for the result.
    userGesture: Optional[bool]
            Whether execution should be treated as initiated by user in the UI.
    awaitPromise: Optional[bool]
            Whether execution should `await` for resulting value and return once awaited promise is
            resolved.
    executionContextId: Optional[ExecutionContextId]
            Specifies execution context which global object will be used to call function on. Either
            executionContextId or objectId should be specified.
    objectGroup: Optional[str]
            Symbolic group name that can be used to release multiple objects. If objectGroup is not
            specified and objectId is, objectGroup will be inherited from object.

    Returns
    -------
    result: RemoteObject
            Call result.
    exceptionDetails: Optional[ExceptionDetails]
            Exception details.
    """
    response = yield filter_unset_parameters(
        {
            "method": "Runtime.callFunctionOn",
            "params": {
                "functionDeclaration": functionDeclaration,
                "objectId": str(objectId) if objectId else None,
                "arguments": [a.to_json() for a in arguments] if arguments else None,
                "silent": silent,
                "returnByValue": returnByValue,
                "generatePreview": generatePreview,
                "userGesture": userGesture,
                "awaitPromise": awaitPromise,
                "executionContextId": int(executionContextId)
                if executionContextId
                else None,
                "objectGroup": objectGroup,
            },
        }
    )
    return {
        "result": RemoteObject.from_json(response["result"]),
        "exceptionDetails": ExceptionDetails.from_json(response["exceptionDetails"])
        if "exceptionDetails" in response
        else None,
    }


def compile_script(
    expression: str,
    sourceURL: str,
    persistScript: bool,
    executionContextId: Optional[ExecutionContextId] = None,
) -> Generator[dict, dict, dict]:
    """Compiles expression.

    Parameters
    ----------
    expression: str
            Expression to compile.
    sourceURL: str
            Source url to be set for the script.
    persistScript: bool
            Specifies whether the compiled script should be persisted.
    executionContextId: Optional[ExecutionContextId]
            Specifies in which execution context to perform script run. If the parameter is omitted the
            evaluation will be performed in the context of the inspected page.

    Returns
    -------
    scriptId: Optional[ScriptId]
            Id of the script.
    exceptionDetails: Optional[ExceptionDetails]
            Exception details.
    """
    response = yield filter_unset_parameters(
        {
            "method": "Runtime.compileScript",
            "params": {
                "expression": expression,
                "sourceURL": sourceURL,
                "persistScript": persistScript,
                "executionContextId": int(executionContextId)
                if executionContextId
                else None,
            },
        }
    )
    return {
        "scriptId": ScriptId(response["scriptId"]) if "scriptId" in response else None,
        "exceptionDetails": ExceptionDetails.from_json(response["exceptionDetails"])
        if "exceptionDetails" in response
        else None,
    }


def disable() -> dict:
    """Disables reporting of execution contexts creation."""
    return {"method": "Runtime.disable", "params": {}}


def discard_console_entries() -> dict:
    """Discards collected exceptions and console API calls."""
    return {"method": "Runtime.discardConsoleEntries", "params": {}}


def enable() -> dict:
    """Enables reporting of execution contexts creation by means of `executionContextCreated` event.
    When the reporting gets enabled the event will be sent immediately for each existing execution
    context.
    """
    return {"method": "Runtime.enable", "params": {}}


def evaluate(
    expression: str,
    objectGroup: Optional[str] = None,
    includeCommandLineAPI: Optional[bool] = None,
    silent: Optional[bool] = None,
    contextId: Optional[ExecutionContextId] = None,
    returnByValue: Optional[bool] = None,
    generatePreview: Optional[bool] = None,
    userGesture: Optional[bool] = None,
    awaitPromise: Optional[bool] = None,
    throwOnSideEffect: Optional[bool] = None,
    timeout: Optional[TimeDelta] = None,
    disableBreaks: Optional[bool] = None,
    replMode: Optional[bool] = None,
    allowUnsafeEvalBlockedByCSP: Optional[bool] = None,
) -> Generator[dict, dict, dict]:
    """Evaluates expression on global object.

    Parameters
    ----------
    expression: str
            Expression to evaluate.
    objectGroup: Optional[str]
            Symbolic group name that can be used to release multiple objects.
    includeCommandLineAPI: Optional[bool]
            Determines whether Command Line API should be available during the evaluation.
    silent: Optional[bool]
            In silent mode exceptions thrown during evaluation are not reported and do not pause
            execution. Overrides `setPauseOnException` state.
    contextId: Optional[ExecutionContextId]
            Specifies in which execution context to perform evaluation. If the parameter is omitted the
            evaluation will be performed in the context of the inspected page.
    returnByValue: Optional[bool]
            Whether the result is expected to be a JSON object that should be sent by value.
    generatePreview: Optional[bool]
            Whether preview should be generated for the result.
    userGesture: Optional[bool]
            Whether execution should be treated as initiated by user in the UI.
    awaitPromise: Optional[bool]
            Whether execution should `await` for resulting value and return once awaited promise is
            resolved.
    throwOnSideEffect: Optional[bool]
            Whether to throw an exception if side effect cannot be ruled out during evaluation.
            This implies `disableBreaks` below.
    timeout: Optional[TimeDelta]
            Terminate execution after timing out (number of milliseconds).
    disableBreaks: Optional[bool]
            Disable breakpoints during execution.
    replMode: Optional[bool]
            Setting this flag to true enables `let` re-declaration and top-level `await`.
            Note that `let` variables can only be re-declared if they originate from
            `replMode` themselves.
    allowUnsafeEvalBlockedByCSP: Optional[bool]
            The Content Security Policy (CSP) for the target might block 'unsafe-eval'
            which includes eval(), Function(), setTimeout() and setInterval()
            when called with non-callable arguments. This flag bypasses CSP for this
            evaluation and allows unsafe-eval. Defaults to true.

    Returns
    -------
    result: RemoteObject
            Evaluation result.
    exceptionDetails: Optional[ExceptionDetails]
            Exception details.
    """
    response = yield filter_unset_parameters(
        {
            "method": "Runtime.evaluate",
            "params": {
                "expression": expression,
                "objectGroup": objectGroup,
                "includeCommandLineAPI": includeCommandLineAPI,
                "silent": silent,
                "contextId": int(contextId) if contextId else None,
                "returnByValue": returnByValue,
                "generatePreview": generatePreview,
                "userGesture": userGesture,
                "awaitPromise": awaitPromise,
                "throwOnSideEffect": throwOnSideEffect,
                "timeout": float(timeout) if timeout else None,
                "disableBreaks": disableBreaks,
                "replMode": replMode,
                "allowUnsafeEvalBlockedByCSP": allowUnsafeEvalBlockedByCSP,
            },
        }
    )
    return {
        "result": RemoteObject.from_json(response["result"]),
        "exceptionDetails": ExceptionDetails.from_json(response["exceptionDetails"])
        if "exceptionDetails" in response
        else None,
    }


def get_isolate_id() -> Generator[dict, dict, str]:
    """Returns the isolate id.

    **Experimental**

    Returns
    -------
    id: str
            The isolate id.
    """
    response = yield {"method": "Runtime.getIsolateId", "params": {}}
    return response


def get_heap_usage() -> Generator[dict, dict, dict]:
    """Returns the JavaScript heap usage.
    It is the total usage of the corresponding isolate not scoped to a particular Runtime.

    **Experimental**

    Returns
    -------
    usedSize: float
            Used heap size in bytes.
    totalSize: float
            Allocated heap size in bytes.
    """
    response = yield {"method": "Runtime.getHeapUsage", "params": {}}
    return {"usedSize": response["usedSize"], "totalSize": response["totalSize"]}


def get_properties(
    objectId: RemoteObjectId,
    ownProperties: Optional[bool] = None,
    accessorPropertiesOnly: Optional[bool] = None,
    generatePreview: Optional[bool] = None,
) -> Generator[dict, dict, dict]:
    """Returns properties of a given object. Object group of the result is inherited from the target
    object.

    Parameters
    ----------
    objectId: RemoteObjectId
            Identifier of the object to return properties for.
    ownProperties: Optional[bool]
            If true, returns properties belonging only to the element itself, not to its prototype
            chain.
    accessorPropertiesOnly: Optional[bool]
            If true, returns accessor properties (with getter/setter) only; internal properties are not
            returned either.
    generatePreview: Optional[bool]
            Whether preview should be generated for the results.

    Returns
    -------
    result: list[PropertyDescriptor]
            Object properties.
    internalProperties: Optional[list[InternalPropertyDescriptor]]
            Internal object properties (only of the element itself).
    privateProperties: Optional[list[PrivatePropertyDescriptor]]
            Object private properties.
    exceptionDetails: Optional[ExceptionDetails]
            Exception details.
    """
    response = yield filter_unset_parameters(
        {
            "method": "Runtime.getProperties",
            "params": {
                "objectId": str(objectId),
                "ownProperties": ownProperties,
                "accessorPropertiesOnly": accessorPropertiesOnly,
                "generatePreview": generatePreview,
            },
        }
    )
    return {
        "result": [PropertyDescriptor.from_json(r) for r in response["result"]],
        "internalProperties": [
            InternalPropertyDescriptor.from_json(i)
            for i in response["internalProperties"]
        ]
        if "internalProperties" in response
        else None,
        "privateProperties": [
            PrivatePropertyDescriptor.from_json(p)
            for p in response["privateProperties"]
        ]
        if "privateProperties" in response
        else None,
        "exceptionDetails": ExceptionDetails.from_json(response["exceptionDetails"])
        if "exceptionDetails" in response
        else None,
    }


def global_lexical_scope_names(
    executionContextId: Optional[ExecutionContextId] = None,
) -> Generator[dict, dict, list[str]]:
    """Returns all let, const and class variables from global scope.

    Parameters
    ----------
    executionContextId: Optional[ExecutionContextId]
            Specifies in which execution context to lookup global scope variables.

    Returns
    -------
    names: list[str]
    """
    response = yield filter_unset_parameters(
        {
            "method": "Runtime.globalLexicalScopeNames",
            "params": {
                "executionContextId": int(executionContextId)
                if executionContextId
                else None
            },
        }
    )
    return response


def query_objects(
    prototypeObjectId: RemoteObjectId, objectGroup: Optional[str] = None
) -> Generator[dict, dict, RemoteObject]:
    """
    Parameters
    ----------
    prototypeObjectId: RemoteObjectId
            Identifier of the prototype to return objects for.
    objectGroup: Optional[str]
            Symbolic group name that can be used to release the results.

    Returns
    -------
    objects: RemoteObject
            Array with objects.
    """
    response = yield filter_unset_parameters(
        {
            "method": "Runtime.queryObjects",
            "params": {
                "prototypeObjectId": str(prototypeObjectId),
                "objectGroup": objectGroup,
            },
        }
    )
    return RemoteObject.from_json(response)


def release_object(objectId: RemoteObjectId) -> dict:
    """Releases remote object with given id.

    Parameters
    ----------
    objectId: RemoteObjectId
            Identifier of the object to release.
    """
    return {"method": "Runtime.releaseObject", "params": {"objectId": str(objectId)}}


def release_object_group(objectGroup: str) -> dict:
    """Releases all remote objects that belong to a given group.

    Parameters
    ----------
    objectGroup: str
            Symbolic object group name.
    """
    return {
        "method": "Runtime.releaseObjectGroup",
        "params": {"objectGroup": objectGroup},
    }


def run_if_waiting_for_debugger() -> dict:
    """Tells inspected instance to run if it was waiting for debugger to attach."""
    return {"method": "Runtime.runIfWaitingForDebugger", "params": {}}


def run_script(
    scriptId: ScriptId,
    executionContextId: Optional[ExecutionContextId] = None,
    objectGroup: Optional[str] = None,
    silent: Optional[bool] = None,
    includeCommandLineAPI: Optional[bool] = None,
    returnByValue: Optional[bool] = None,
    generatePreview: Optional[bool] = None,
    awaitPromise: Optional[bool] = None,
) -> Generator[dict, dict, dict]:
    """Runs script with given id in a given context.

    Parameters
    ----------
    scriptId: ScriptId
            Id of the script to run.
    executionContextId: Optional[ExecutionContextId]
            Specifies in which execution context to perform script run. If the parameter is omitted the
            evaluation will be performed in the context of the inspected page.
    objectGroup: Optional[str]
            Symbolic group name that can be used to release multiple objects.
    silent: Optional[bool]
            In silent mode exceptions thrown during evaluation are not reported and do not pause
            execution. Overrides `setPauseOnException` state.
    includeCommandLineAPI: Optional[bool]
            Determines whether Command Line API should be available during the evaluation.
    returnByValue: Optional[bool]
            Whether the result is expected to be a JSON object which should be sent by value.
    generatePreview: Optional[bool]
            Whether preview should be generated for the result.
    awaitPromise: Optional[bool]
            Whether execution should `await` for resulting value and return once awaited promise is
            resolved.

    Returns
    -------
    result: RemoteObject
            Run result.
    exceptionDetails: Optional[ExceptionDetails]
            Exception details.
    """
    response = yield filter_unset_parameters(
        {
            "method": "Runtime.runScript",
            "params": {
                "scriptId": str(scriptId),
                "executionContextId": int(executionContextId)
                if executionContextId
                else None,
                "objectGroup": objectGroup,
                "silent": silent,
                "includeCommandLineAPI": includeCommandLineAPI,
                "returnByValue": returnByValue,
                "generatePreview": generatePreview,
                "awaitPromise": awaitPromise,
            },
        }
    )
    return {
        "result": RemoteObject.from_json(response["result"]),
        "exceptionDetails": ExceptionDetails.from_json(response["exceptionDetails"])
        if "exceptionDetails" in response
        else None,
    }


def set_async_call_stack_depth(maxDepth: int) -> dict:
    """Enables or disables async call stacks tracking.

    Parameters
    ----------
    maxDepth: int
            Maximum depth of async call stacks. Setting to `0` will effectively disable collecting async
            call stacks (default).
    """
    return {
        "method": "Runtime.setAsyncCallStackDepth",
        "params": {"maxDepth": maxDepth},
    }


def set_custom_object_formatter_enabled(enabled: bool) -> dict:
    """
    **Experimental**

    Parameters
    ----------
    enabled: bool
    """
    return {
        "method": "Runtime.setCustomObjectFormatterEnabled",
        "params": {"enabled": enabled},
    }


def set_max_call_stack_size_to_capture(size: int) -> dict:
    """
    **Experimental**

    Parameters
    ----------
    size: int
    """
    return {"method": "Runtime.setMaxCallStackSizeToCapture", "params": {"size": size}}


def terminate_execution() -> dict:
    """Terminate current or next JavaScript execution.
    Will cancel the termination when the outer-most script execution ends.

    **Experimental**
    """
    return {"method": "Runtime.terminateExecution", "params": {}}


def add_binding(
    name: str, executionContextId: Optional[ExecutionContextId] = None
) -> dict:
    """If executionContextId is empty, adds binding with the given name on the
    global objects of all inspected contexts, including those created later,
    bindings survive reloads.
    If executionContextId is specified, adds binding only on global object of
    given execution context.
    Binding function takes exactly one argument, this argument should be string,
    in case of any other input, function throws an exception.
    Each binding function call produces Runtime.bindingCalled notification.

    **Experimental**

    Parameters
    ----------
    name: str
    executionContextId: Optional[ExecutionContextId]
    """
    return filter_unset_parameters(
        {
            "method": "Runtime.addBinding",
            "params": {
                "name": name,
                "executionContextId": int(executionContextId)
                if executionContextId
                else None,
            },
        }
    )


def remove_binding(name: str) -> dict:
    """This method does not remove binding function from global object but
    unsubscribes current runtime agent from Runtime.bindingCalled notifications.

    **Experimental**

    Parameters
    ----------
    name: str
    """
    return {"method": "Runtime.removeBinding", "params": {"name": name}}


@dataclasses.dataclass
class BindingCalled:
    """Notification is issued every time when binding is called.

    Attributes
    ----------
    name: str
    payload: str
    executionContextId: ExecutionContextId
            Identifier of the context where the call was made.
    """

    name: str
    payload: str
    executionContextId: ExecutionContextId

    @classmethod
    def from_json(cls, json: dict) -> BindingCalled:
        return cls(
            json["name"],
            json["payload"],
            ExecutionContextId(json["executionContextId"]),
        )


@dataclasses.dataclass
class ConsoleAPICalled:
    """Issued when console API was called.

    Attributes
    ----------
    type: str
            Type of the call.
    args: list[RemoteObject]
            Call arguments.
    executionContextId: ExecutionContextId
            Identifier of the context where the call was made.
    timestamp: Timestamp
            Call timestamp.
    stackTrace: Optional[StackTrace]
            Stack trace captured when the call was made. The async stack chain is automatically reported for
            the following call types: `assert`, `error`, `trace`, `warning`. For other types the async call
            chain can be retrieved using `Debugger.getStackTrace` and `stackTrace.parentId` field.
    context: Optional[str]
            Console context descriptor for calls on non-default console context (not console.*):
            'anonymous#unique-logger-id' for call on unnamed context, 'name#unique-logger-id' for call
            on named context.
    """

    type: str
    args: list[RemoteObject]
    executionContextId: ExecutionContextId
    timestamp: Timestamp
    stackTrace: Optional[StackTrace] = None
    context: Optional[str] = None

    @classmethod
    def from_json(cls, json: dict) -> ConsoleAPICalled:
        return cls(
            json["type"],
            [RemoteObject.from_json(a) for a in json["args"]],
            ExecutionContextId(json["executionContextId"]),
            Timestamp(json["timestamp"]),
            StackTrace.from_json(json["stackTrace"]) if "stackTrace" in json else None,
            json.get("context"),
        )


@dataclasses.dataclass
class ExceptionRevoked:
    """Issued when unhandled exception was revoked.

    Attributes
    ----------
    reason: str
            Reason describing why exception was revoked.
    exceptionId: int
            The id of revoked exception, as reported in `exceptionThrown`.
    """

    reason: str
    exceptionId: int

    @classmethod
    def from_json(cls, json: dict) -> ExceptionRevoked:
        return cls(json["reason"], json["exceptionId"])


@dataclasses.dataclass
class ExceptionThrown:
    """Issued when exception was thrown and unhandled.

    Attributes
    ----------
    timestamp: Timestamp
            Timestamp of the exception.
    exceptionDetails: ExceptionDetails
    """

    timestamp: Timestamp
    exceptionDetails: ExceptionDetails

    @classmethod
    def from_json(cls, json: dict) -> ExceptionThrown:
        return cls(
            Timestamp(json["timestamp"]),
            ExceptionDetails.from_json(json["exceptionDetails"]),
        )


@dataclasses.dataclass
class ExecutionContextCreated:
    """Issued when new execution context is created.

    Attributes
    ----------
    context: ExecutionContextDescription
            A newly created execution context.
    """

    context: ExecutionContextDescription

    @classmethod
    def from_json(cls, json: dict) -> ExecutionContextCreated:
        return cls(ExecutionContextDescription.from_json(json["context"]))


@dataclasses.dataclass
class ExecutionContextDestroyed:
    """Issued when execution context is destroyed.

    Attributes
    ----------
    executionContextId: ExecutionContextId
            Id of the destroyed context
    """

    executionContextId: ExecutionContextId

    @classmethod
    def from_json(cls, json: dict) -> ExecutionContextDestroyed:
        return cls(ExecutionContextId(json["executionContextId"]))


@dataclasses.dataclass
class ExecutionContextsCleared:
    """Issued when all executionContexts were cleared in browser"""

    @classmethod
    def from_json(cls, json: dict) -> ExecutionContextsCleared:
        return cls()


@dataclasses.dataclass
class InspectRequested:
    """Issued when object should be inspected (for example, as a result of inspect() command line API
    call).

    Attributes
    ----------
    object: RemoteObject
    hints: dict
    """

    object: RemoteObject
    hints: dict

    @classmethod
    def from_json(cls, json: dict) -> InspectRequested:
        return cls(RemoteObject.from_json(json["object"]), json["hints"])
