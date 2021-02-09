from __future__ import annotations

import dataclasses
import enum
from typing import Optional

from . import dom, runtime
from .common import filter_none, filter_unset_parameters


class AXNodeId(str):
    """Unique accessibility node identifier."""

    def __repr__(self):
        return f"AXNodeId({super().__repr__()})"


class AXValueType(enum.Enum):
    """Enum of possible property types."""

    BOOLEAN = "boolean"
    TRISTATE = "tristate"
    BOOLEAN_OR_UNDEFINED = "booleanOrUndefined"
    IDREF = "idref"
    IDREF_LIST = "idrefList"
    INTEGER = "integer"
    NODE = "node"
    NODE_LIST = "nodeList"
    NUMBER = "number"
    STRING = "string"
    COMPUTED_STRING = "computedString"
    TOKEN = "token"
    TOKEN_LIST = "tokenList"
    DOM_RELATION = "domRelation"
    ROLE = "role"
    INTERNAL_ROLE = "internalRole"
    VALUE_UNDEFINED = "valueUndefined"


class AXValueSourceType(enum.Enum):
    """Enum of possible property sources."""

    ATTRIBUTE = "attribute"
    IMPLICIT = "implicit"
    STYLE = "style"
    CONTENTS = "contents"
    PLACEHOLDER = "placeholder"
    RELATED_ELEMENT = "relatedElement"


class AXValueNativeSourceType(enum.Enum):
    """Enum of possible native property sources (as a subtype of a particular AXValueSourceType)."""

    FIGCAPTION = "figcaption"
    LABEL = "label"
    LABELFOR = "labelfor"
    LABELWRAPPED = "labelwrapped"
    LEGEND = "legend"
    RUBYANNOTATION = "rubyannotation"
    TABLECAPTION = "tablecaption"
    TITLE = "title"
    OTHER = "other"


@dataclasses.dataclass
class AXValueSource:
    """A single source for a computed AX property.

    Attributes
    ----------
    type: AXValueSourceType
            What type of source this is.
    value: Optional[AXValue]
            The value of this property source.
    attribute: Optional[str]
            The name of the relevant attribute, if any.
    attributeValue: Optional[AXValue]
            The value of the relevant attribute, if any.
    superseded: Optional[bool]
            Whether this source is superseded by a higher priority source.
    nativeSource: Optional[AXValueNativeSourceType]
            The native markup source for this value, e.g. a <label> element.
    nativeSourceValue: Optional[AXValue]
            The value, such as a node or node list, of the native source.
    invalid: Optional[bool]
            Whether the value for this property is invalid.
    invalidReason: Optional[str]
            Reason for the value being invalid, if it is.
    """

    type: AXValueSourceType
    value: Optional[AXValue] = None
    attribute: Optional[str] = None
    attributeValue: Optional[AXValue] = None
    superseded: Optional[bool] = None
    nativeSource: Optional[AXValueNativeSourceType] = None
    nativeSourceValue: Optional[AXValue] = None
    invalid: Optional[bool] = None
    invalidReason: Optional[str] = None

    @classmethod
    def from_json(cls, json: dict) -> AXValueSource:
        return cls(
            AXValueSourceType(json["type"]),
            AXValue.from_json(json["value"]) if "value" in json else None,
            json.get("attribute"),
            AXValue.from_json(json["attributeValue"])
            if "attributeValue" in json
            else None,
            json.get("superseded"),
            AXValueNativeSourceType(json["nativeSource"])
            if "nativeSource" in json
            else None,
            AXValue.from_json(json["nativeSourceValue"])
            if "nativeSourceValue" in json
            else None,
            json.get("invalid"),
            json.get("invalidReason"),
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "type": self.type.value,
                "value": self.value.to_json() if self.value else None,
                "attribute": self.attribute,
                "attributeValue": self.attributeValue.to_json()
                if self.attributeValue
                else None,
                "superseded": self.superseded,
                "nativeSource": self.nativeSource.value if self.nativeSource else None,
                "nativeSourceValue": self.nativeSourceValue.to_json()
                if self.nativeSourceValue
                else None,
                "invalid": self.invalid,
                "invalidReason": self.invalidReason,
            }
        )


@dataclasses.dataclass
class AXRelatedNode:
    """
    Attributes
    ----------
    backendDOMNodeId: dom.BackendNodeId
            The BackendNodeId of the related DOM node.
    idref: Optional[str]
            The IDRef value provided, if any.
    text: Optional[str]
            The text alternative of this node in the current context.
    """

    backendDOMNodeId: dom.BackendNodeId
    idref: Optional[str] = None
    text: Optional[str] = None

    @classmethod
    def from_json(cls, json: dict) -> AXRelatedNode:
        return cls(
            dom.BackendNodeId(json["backendDOMNodeId"]),
            json.get("idref"),
            json.get("text"),
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "backendDOMNodeId": int(self.backendDOMNodeId),
                "idref": self.idref,
                "text": self.text,
            }
        )


@dataclasses.dataclass
class AXProperty:
    """
    Attributes
    ----------
    name: AXPropertyName
            The name of this property.
    value: AXValue
            The value of this property.
    """

    name: AXPropertyName
    value: AXValue

    @classmethod
    def from_json(cls, json: dict) -> AXProperty:
        return cls(AXPropertyName(json["name"]), AXValue.from_json(json["value"]))

    def to_json(self) -> dict:
        return {"name": self.name.value, "value": self.value.to_json()}


@dataclasses.dataclass
class AXValue:
    """A single computed AX property.

    Attributes
    ----------
    type: AXValueType
            The type of this value.
    value: Optional[any]
            The computed value of this property.
    relatedNodes: Optional[list[AXRelatedNode]]
            One or more related nodes, if applicable.
    sources: Optional[list[AXValueSource]]
            The sources which contributed to the computation of this property.
    """

    type: AXValueType
    value: Optional[any] = None
    relatedNodes: Optional[list[AXRelatedNode]] = None
    sources: Optional[list[AXValueSource]] = None

    @classmethod
    def from_json(cls, json: dict) -> AXValue:
        return cls(
            AXValueType(json["type"]),
            json.get("value"),
            [AXRelatedNode.from_json(r) for r in json["relatedNodes"]]
            if "relatedNodes" in json
            else None,
            [AXValueSource.from_json(s) for s in json["sources"]]
            if "sources" in json
            else None,
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "type": self.type.value,
                "value": self.value,
                "relatedNodes": [r.to_json() for r in self.relatedNodes]
                if self.relatedNodes
                else None,
                "sources": [s.to_json() for s in self.sources]
                if self.sources
                else None,
            }
        )


class AXPropertyName(enum.Enum):
    """Values of AXProperty name:
    - from 'busy' to 'roledescription': states which apply to every AX node
    - from 'live' to 'root': attributes which apply to nodes in live regions
    - from 'autocomplete' to 'valuetext': attributes which apply to widgets
    - from 'checked' to 'selected': states which apply to widgets
    - from 'activedescendant' to 'owns' - relationships between elements other than parent/child/sibling.
    """

    BUSY = "busy"
    DISABLED = "disabled"
    EDITABLE = "editable"
    FOCUSABLE = "focusable"
    FOCUSED = "focused"
    HIDDEN = "hidden"
    HIDDEN_ROOT = "hiddenRoot"
    INVALID = "invalid"
    KEYSHORTCUTS = "keyshortcuts"
    SETTABLE = "settable"
    ROLEDESCRIPTION = "roledescription"
    LIVE = "live"
    ATOMIC = "atomic"
    RELEVANT = "relevant"
    ROOT = "root"
    AUTOCOMPLETE = "autocomplete"
    HAS_POPUP = "hasPopup"
    LEVEL = "level"
    MULTISELECTABLE = "multiselectable"
    ORIENTATION = "orientation"
    MULTILINE = "multiline"
    READONLY = "readonly"
    REQUIRED = "required"
    VALUEMIN = "valuemin"
    VALUEMAX = "valuemax"
    VALUETEXT = "valuetext"
    CHECKED = "checked"
    EXPANDED = "expanded"
    MODAL = "modal"
    PRESSED = "pressed"
    SELECTED = "selected"
    ACTIVEDESCENDANT = "activedescendant"
    CONTROLS = "controls"
    DESCRIBEDBY = "describedby"
    DETAILS = "details"
    ERRORMESSAGE = "errormessage"
    FLOWTO = "flowto"
    LABELLEDBY = "labelledby"
    OWNS = "owns"


@dataclasses.dataclass
class AXNode:
    """A node in the accessibility tree.

    Attributes
    ----------
    nodeId: AXNodeId
            Unique identifier for this node.
    ignored: bool
            Whether this node is ignored for accessibility
    ignoredReasons: Optional[list[AXProperty]]
            Collection of reasons why this node is hidden.
    role: Optional[AXValue]
            This `Node`'s role, whether explicit or implicit.
    name: Optional[AXValue]
            The accessible name for this `Node`.
    description: Optional[AXValue]
            The accessible description for this `Node`.
    value: Optional[AXValue]
            The value for this `Node`.
    properties: Optional[list[AXProperty]]
            All other properties
    childIds: Optional[list[AXNodeId]]
            IDs for each of this node's child nodes.
    backendDOMNodeId: Optional[dom.BackendNodeId]
            The backend ID for the associated DOM node, if any.
    """

    nodeId: AXNodeId
    ignored: bool
    ignoredReasons: Optional[list[AXProperty]] = None
    role: Optional[AXValue] = None
    name: Optional[AXValue] = None
    description: Optional[AXValue] = None
    value: Optional[AXValue] = None
    properties: Optional[list[AXProperty]] = None
    childIds: Optional[list[AXNodeId]] = None
    backendDOMNodeId: Optional[dom.BackendNodeId] = None

    @classmethod
    def from_json(cls, json: dict) -> AXNode:
        return cls(
            AXNodeId(json["nodeId"]),
            json["ignored"],
            [AXProperty.from_json(i) for i in json["ignoredReasons"]]
            if "ignoredReasons" in json
            else None,
            AXValue.from_json(json["role"]) if "role" in json else None,
            AXValue.from_json(json["name"]) if "name" in json else None,
            AXValue.from_json(json["description"]) if "description" in json else None,
            AXValue.from_json(json["value"]) if "value" in json else None,
            [AXProperty.from_json(p) for p in json["properties"]]
            if "properties" in json
            else None,
            [AXNodeId(c) for c in json["childIds"]] if "childIds" in json else None,
            dom.BackendNodeId(json["backendDOMNodeId"])
            if "backendDOMNodeId" in json
            else None,
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "nodeId": str(self.nodeId),
                "ignored": self.ignored,
                "ignoredReasons": [i.to_json() for i in self.ignoredReasons]
                if self.ignoredReasons
                else None,
                "role": self.role.to_json() if self.role else None,
                "name": self.name.to_json() if self.name else None,
                "description": self.description.to_json() if self.description else None,
                "value": self.value.to_json() if self.value else None,
                "properties": [p.to_json() for p in self.properties]
                if self.properties
                else None,
                "childIds": [str(c) for c in self.childIds] if self.childIds else None,
                "backendDOMNodeId": int(self.backendDOMNodeId)
                if self.backendDOMNodeId
                else None,
            }
        )


def disable():
    """Disables the accessibility domain."""
    return {"method": "Accessibility.disable", "params": {}}


def enable():
    """Enables the accessibility domain which causes `AXNodeId`s to remain consistent between method calls.
    This turns on accessibility for the page, which can impact performance until accessibility is disabled.
    """
    return {"method": "Accessibility.enable", "params": {}}


def get_partial_ax_tree(
    nodeId: Optional[dom.NodeId] = None,
    backendNodeId: Optional[dom.BackendNodeId] = None,
    objectId: Optional[runtime.RemoteObjectId] = None,
    fetchRelatives: Optional[bool] = None,
):
    """Fetches the accessibility node and partial accessibility tree for this DOM node, if it exists.

    **Experimental**

    Parameters
    ----------
    nodeId: Optional[dom.NodeId]
            Identifier of the node to get the partial accessibility tree for.
    backendNodeId: Optional[dom.BackendNodeId]
            Identifier of the backend node to get the partial accessibility tree for.
    objectId: Optional[runtime.RemoteObjectId]
            JavaScript object id of the node wrapper to get the partial accessibility tree for.
    fetchRelatives: Optional[bool]
            Whether to fetch this nodes ancestors, siblings and children. Defaults to true.

    Returns
    -------
    nodes: list[AXNode]
            The `Accessibility.AXNode` for this DOM node, if it exists, plus its ancestors, siblings and
            children, if requested.
    """
    return filter_unset_parameters(
        {
            "method": "Accessibility.getPartialAXTree",
            "params": {
                "nodeId": nodeId,
                "backendNodeId": backendNodeId,
                "objectId": objectId,
                "fetchRelatives": fetchRelatives,
            },
        }
    )


def get_full_ax_tree(max_depth: Optional[int] = None):
    """Fetches the entire accessibility tree for the root Document

    **Experimental**

    Parameters
    ----------
    max_depth: Optional[int]
            The maximum depth at which descendants of the root node should be retrieved.
            If omitted, the full tree is returned.

    Returns
    -------
    nodes: list[AXNode]
    """
    return filter_unset_parameters(
        {"method": "Accessibility.getFullAXTree", "params": {"max_depth": max_depth}}
    )


def get_child_ax_nodes(id: AXNodeId):
    """Fetches a particular accessibility node by AXNodeId.
    Requires `enable()` to have been called previously.

    **Experimental**

    Parameters
    ----------
    id: AXNodeId

    Returns
    -------
    nodes: list[AXNode]
    """
    return {"method": "Accessibility.getChildAXNodes", "params": {"id": id}}


def query_ax_tree(
    nodeId: Optional[dom.NodeId] = None,
    backendNodeId: Optional[dom.BackendNodeId] = None,
    objectId: Optional[runtime.RemoteObjectId] = None,
    accessibleName: Optional[str] = None,
    role: Optional[str] = None,
):
    """Query a DOM node's accessibility subtree for accessible name and role.
    This command computes the name and role for all nodes in the subtree, including those that are
    ignored for accessibility, and returns those that mactch the specified name and role. If no DOM
    node is specified, or the DOM node does not exist, the command returns an error. If neither
    `accessibleName` or `role` is specified, it returns all the accessibility nodes in the subtree.

    **Experimental**

    Parameters
    ----------
    nodeId: Optional[dom.NodeId]
            Identifier of the node for the root to query.
    backendNodeId: Optional[dom.BackendNodeId]
            Identifier of the backend node for the root to query.
    objectId: Optional[runtime.RemoteObjectId]
            JavaScript object id of the node wrapper for the root to query.
    accessibleName: Optional[str]
            Find nodes with this computed name.
    role: Optional[str]
            Find nodes with this computed role.

    Returns
    -------
    nodes: list[AXNode]
            A list of `Accessibility.AXNode` matching the specified attributes,
            including nodes that are ignored for accessibility.
    """
    return filter_unset_parameters(
        {
            "method": "Accessibility.queryAXTree",
            "params": {
                "nodeId": nodeId,
                "backendNodeId": backendNodeId,
                "objectId": objectId,
                "accessibleName": accessibleName,
                "role": role,
            },
        }
    )
