from __future__ import annotations

import dataclasses
import enum
from typing import Generator, Optional

from deprecated.sphinx import deprecated

from . import page, runtime
from .common import filter_none


class NodeId(int):
    """Unique DOM node identifier."""

    def __repr__(self):
        return f"NodeId({super().__repr__()})"


class BackendNodeId(int):
    """Unique DOM node identifier used to reference a node that may not have been pushed to the
    front-end.
    """

    def __repr__(self):
        return f"BackendNodeId({super().__repr__()})"


@dataclasses.dataclass
class BackendNode:
    """Backend node with a friendly name.

    Attributes
    ----------
    nodeType: int
            `Node`'s nodeType.
    nodeName: str
            `Node`'s nodeName.
    backendNodeId: BackendNodeId
    """

    nodeType: int
    nodeName: str
    backendNodeId: BackendNodeId

    @classmethod
    def from_json(cls, json: dict) -> BackendNode:
        return cls(
            json["nodeType"], json["nodeName"], BackendNodeId(json["backendNodeId"])
        )

    def to_json(self) -> dict:
        return {
            "nodeType": self.nodeType,
            "nodeName": self.nodeName,
            "backendNodeId": int(self.backendNodeId),
        }


class PseudoType(enum.Enum):
    """Pseudo element type."""

    FIRST_LINE = "first-line"
    FIRST_LETTER = "first-letter"
    BEFORE = "before"
    AFTER = "after"
    MARKER = "marker"
    BACKDROP = "backdrop"
    SELECTION = "selection"
    TARGET_TEXT = "target-text"
    SPELLING_ERROR = "spelling-error"
    GRAMMAR_ERROR = "grammar-error"
    FIRST_LINE_INHERITED = "first-line-inherited"
    SCROLLBAR = "scrollbar"
    SCROLLBAR_THUMB = "scrollbar-thumb"
    SCROLLBAR_BUTTON = "scrollbar-button"
    SCROLLBAR_TRACK = "scrollbar-track"
    SCROLLBAR_TRACK_PIECE = "scrollbar-track-piece"
    SCROLLBAR_CORNER = "scrollbar-corner"
    RESIZER = "resizer"
    INPUT_LIST_BUTTON = "input-list-button"


class ShadowRootType(enum.Enum):
    """Shadow root type."""

    USER_AGENT = "user-agent"
    OPEN = "open"
    CLOSED = "closed"


@dataclasses.dataclass
class Node:
    """DOM interaction is implemented in terms of mirror objects that represent the actual DOM nodes.
    DOMNode is a base node mirror type.

    Attributes
    ----------
    nodeId: NodeId
            Node identifier that is passed into the rest of the DOM messages as the `nodeId`. Backend
            will only push node with given `id` once. It is aware of all requested nodes and will only
            fire DOM events for nodes known to the client.
    backendNodeId: BackendNodeId
            The BackendNodeId for this node.
    nodeType: int
            `Node`'s nodeType.
    nodeName: str
            `Node`'s nodeName.
    localName: str
            `Node`'s localName.
    nodeValue: str
            `Node`'s nodeValue.
    parentId: Optional[NodeId]
            The id of the parent node if any.
    childNodeCount: Optional[int]
            Child count for `Container` nodes.
    children: Optional[list[Node]]
            Child nodes of this node when requested with children.
    attributes: Optional[list[str]]
            Attributes of the `Element` node in the form of flat array `[name1, value1, name2, value2]`.
    documentURL: Optional[str]
            Document URL that `Document` or `FrameOwner` node points to.
    baseURL: Optional[str]
            Base URL that `Document` or `FrameOwner` node uses for URL completion.
    publicId: Optional[str]
            `DocumentType`'s publicId.
    systemId: Optional[str]
            `DocumentType`'s systemId.
    internalSubset: Optional[str]
            `DocumentType`'s internalSubset.
    xmlVersion: Optional[str]
            `Document`'s XML version in case of XML documents.
    name: Optional[str]
            `Attr`'s name.
    value: Optional[str]
            `Attr`'s value.
    pseudoType: Optional[PseudoType]
            Pseudo element type for this node.
    shadowRootType: Optional[ShadowRootType]
            Shadow root type.
    frameId: Optional[page.FrameId]
            Frame ID for frame owner elements.
    contentDocument: Optional[Node]
            Content document for frame owner elements.
    shadowRoots: Optional[list[Node]]
            Shadow root list for given element host.
    templateContent: Optional[Node]
            Content document fragment for template elements.
    pseudoElements: Optional[list[Node]]
            Pseudo elements associated with this node.
    importedDocument: Optional[Node]
            Import document for the HTMLImport links.
    distributedNodes: Optional[list[BackendNode]]
            Distributed nodes for given insertion point.
    isSVG: Optional[bool]
            Whether the node is SVG.
    """

    nodeId: NodeId
    backendNodeId: BackendNodeId
    nodeType: int
    nodeName: str
    localName: str
    nodeValue: str
    parentId: Optional[NodeId] = None
    childNodeCount: Optional[int] = None
    children: Optional[list[Node]] = None
    attributes: Optional[list[str]] = None
    documentURL: Optional[str] = None
    baseURL: Optional[str] = None
    publicId: Optional[str] = None
    systemId: Optional[str] = None
    internalSubset: Optional[str] = None
    xmlVersion: Optional[str] = None
    name: Optional[str] = None
    value: Optional[str] = None
    pseudoType: Optional[PseudoType] = None
    shadowRootType: Optional[ShadowRootType] = None
    frameId: Optional[page.FrameId] = None
    contentDocument: Optional[Node] = None
    shadowRoots: Optional[list[Node]] = None
    templateContent: Optional[Node] = None
    pseudoElements: Optional[list[Node]] = None
    importedDocument: Optional[Node] = None
    distributedNodes: Optional[list[BackendNode]] = None
    isSVG: Optional[bool] = None

    @classmethod
    def from_json(cls, json: dict) -> Node:
        return cls(
            NodeId(json["nodeId"]),
            BackendNodeId(json["backendNodeId"]),
            json["nodeType"],
            json["nodeName"],
            json["localName"],
            json["nodeValue"],
            NodeId(json["parentId"]) if "parentId" in json else None,
            json.get("childNodeCount"),
            [Node.from_json(c) for c in json["children"]]
            if "children" in json
            else None,
            json.get("attributes"),
            json.get("documentURL"),
            json.get("baseURL"),
            json.get("publicId"),
            json.get("systemId"),
            json.get("internalSubset"),
            json.get("xmlVersion"),
            json.get("name"),
            json.get("value"),
            PseudoType(json["pseudoType"]) if "pseudoType" in json else None,
            ShadowRootType(json["shadowRootType"])
            if "shadowRootType" in json
            else None,
            page.FrameId(json["frameId"]) if "frameId" in json else None,
            Node.from_json(json["contentDocument"])
            if "contentDocument" in json
            else None,
            [Node.from_json(s) for s in json["shadowRoots"]]
            if "shadowRoots" in json
            else None,
            Node.from_json(json["templateContent"])
            if "templateContent" in json
            else None,
            [Node.from_json(p) for p in json["pseudoElements"]]
            if "pseudoElements" in json
            else None,
            Node.from_json(json["importedDocument"])
            if "importedDocument" in json
            else None,
            [BackendNode.from_json(d) for d in json["distributedNodes"]]
            if "distributedNodes" in json
            else None,
            json.get("isSVG"),
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "nodeId": int(self.nodeId),
                "backendNodeId": int(self.backendNodeId),
                "nodeType": self.nodeType,
                "nodeName": self.nodeName,
                "localName": self.localName,
                "nodeValue": self.nodeValue,
                "parentId": int(self.parentId) if self.parentId else None,
                "childNodeCount": self.childNodeCount,
                "children": [c.to_json() for c in self.children]
                if self.children
                else None,
                "attributes": self.attributes,
                "documentURL": self.documentURL,
                "baseURL": self.baseURL,
                "publicId": self.publicId,
                "systemId": self.systemId,
                "internalSubset": self.internalSubset,
                "xmlVersion": self.xmlVersion,
                "name": self.name,
                "value": self.value,
                "pseudoType": self.pseudoType.value if self.pseudoType else None,
                "shadowRootType": self.shadowRootType.value
                if self.shadowRootType
                else None,
                "frameId": str(self.frameId) if self.frameId else None,
                "contentDocument": self.contentDocument.to_json()
                if self.contentDocument
                else None,
                "shadowRoots": [s.to_json() for s in self.shadowRoots]
                if self.shadowRoots
                else None,
                "templateContent": self.templateContent.to_json()
                if self.templateContent
                else None,
                "pseudoElements": [p.to_json() for p in self.pseudoElements]
                if self.pseudoElements
                else None,
                "importedDocument": self.importedDocument.to_json()
                if self.importedDocument
                else None,
                "distributedNodes": [d.to_json() for d in self.distributedNodes]
                if self.distributedNodes
                else None,
                "isSVG": self.isSVG,
            }
        )


@dataclasses.dataclass
class RGBA:
    """A structure holding an RGBA color.

    Attributes
    ----------
    r: int
            The red component, in the [0-255] range.
    g: int
            The green component, in the [0-255] range.
    b: int
            The blue component, in the [0-255] range.
    a: Optional[float]
            The alpha component, in the [0-1] range (default: 1).
    """

    r: int
    g: int
    b: int
    a: Optional[float] = None

    @classmethod
    def from_json(cls, json: dict) -> RGBA:
        return cls(json["r"], json["g"], json["b"], json.get("a"))

    def to_json(self) -> dict:
        return filter_none({"r": self.r, "g": self.g, "b": self.b, "a": self.a})


class Quad(list[float]):
    """An array of quad vertices, x immediately followed by y for each point, points clock-wise."""

    def __repr__(self):
        return f"Quad({super().__repr__()})"


@dataclasses.dataclass
class BoxModel:
    """Box model.

    Attributes
    ----------
    content: Quad
            Content box
    padding: Quad
            Padding box
    border: Quad
            Border box
    margin: Quad
            Margin box
    width: int
            Node width
    height: int
            Node height
    shapeOutside: Optional[ShapeOutsideInfo]
            Shape outside coordinates
    """

    content: Quad
    padding: Quad
    border: Quad
    margin: Quad
    width: int
    height: int
    shapeOutside: Optional[ShapeOutsideInfo] = None

    @classmethod
    def from_json(cls, json: dict) -> BoxModel:
        return cls(
            Quad(json["content"]),
            Quad(json["padding"]),
            Quad(json["border"]),
            Quad(json["margin"]),
            json["width"],
            json["height"],
            ShapeOutsideInfo.from_json(json["shapeOutside"])
            if "shapeOutside" in json
            else None,
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "content": list(self.content),
                "padding": list(self.padding),
                "border": list(self.border),
                "margin": list(self.margin),
                "width": self.width,
                "height": self.height,
                "shapeOutside": self.shapeOutside.to_json()
                if self.shapeOutside
                else None,
            }
        )


@dataclasses.dataclass
class ShapeOutsideInfo:
    """CSS Shape Outside details.

    Attributes
    ----------
    bounds: Quad
            Shape bounds
    shape: list[any]
            Shape coordinate details
    marginShape: list[any]
            Margin shape bounds
    """

    bounds: Quad
    shape: list[any]
    marginShape: list[any]

    @classmethod
    def from_json(cls, json: dict) -> ShapeOutsideInfo:
        return cls(Quad(json["bounds"]), json["shape"], json["marginShape"])

    def to_json(self) -> dict:
        return {
            "bounds": list(self.bounds),
            "shape": self.shape,
            "marginShape": self.marginShape,
        }


@dataclasses.dataclass
class Rect:
    """Rectangle.

    Attributes
    ----------
    x: float
            X coordinate
    y: float
            Y coordinate
    width: float
            Rectangle width
    height: float
            Rectangle height
    """

    x: float
    y: float
    width: float
    height: float

    @classmethod
    def from_json(cls, json: dict) -> Rect:
        return cls(json["x"], json["y"], json["width"], json["height"])

    def to_json(self) -> dict:
        return {"x": self.x, "y": self.y, "width": self.width, "height": self.height}


@dataclasses.dataclass
class CSSComputedStyleProperty:
    """
    Attributes
    ----------
    name: str
            Computed style property name.
    value: str
            Computed style property value.
    """

    name: str
    value: str

    @classmethod
    def from_json(cls, json: dict) -> CSSComputedStyleProperty:
        return cls(json["name"], json["value"])

    def to_json(self) -> dict:
        return {"name": self.name, "value": self.value}


def collect_class_names_from_subtree(
    nodeId: NodeId,
) -> Generator[dict, dict, list[str]]:
    """Collects class names for the node with given id and all of it's child nodes.

    Parameters
    ----------
    nodeId: NodeId
            Id of the node to collect class names.

    Returns
    -------
    classNames: list[str]
            Class name list.

    **Experimental**
    """
    response = yield {
        "method": "DOM.collectClassNamesFromSubtree",
        "params": {"nodeId": int(nodeId)},
    }
    return response["classNames"]


def copy_to(
    nodeId: NodeId, targetNodeId: NodeId, insertBeforeNodeId: Optional[NodeId] = None
) -> Generator[dict, dict, NodeId]:
    """Creates a deep copy of the specified node and places it into the target container before the
    given anchor.

    Parameters
    ----------
    nodeId: NodeId
            Id of the node to copy.
    targetNodeId: NodeId
            Id of the element to drop the copy into.
    insertBeforeNodeId: Optional[NodeId]
            Drop the copy before this node (if absent, the copy becomes the last child of
            `targetNodeId`).

    Returns
    -------
    nodeId: NodeId
            Id of the node clone.

    **Experimental**
    """
    response = yield {
        "method": "DOM.copyTo",
        "params": filter_none(
            {
                "nodeId": int(nodeId),
                "targetNodeId": int(targetNodeId),
                "insertBeforeNodeId": int(insertBeforeNodeId)
                if insertBeforeNodeId
                else None,
            }
        ),
    }
    return NodeId(response["nodeId"])


def describe_node(
    nodeId: Optional[NodeId] = None,
    backendNodeId: Optional[BackendNodeId] = None,
    objectId: Optional[runtime.RemoteObjectId] = None,
    depth: Optional[int] = None,
    pierce: Optional[bool] = None,
) -> Generator[dict, dict, Node]:
    """Describes node given its id, does not require domain to be enabled. Does not start tracking any
    objects, can be used for automation.

    Parameters
    ----------
    nodeId: Optional[NodeId]
            Identifier of the node.
    backendNodeId: Optional[BackendNodeId]
            Identifier of the backend node.
    objectId: Optional[runtime.RemoteObjectId]
            JavaScript object id of the node wrapper.
    depth: Optional[int]
            The maximum depth at which children should be retrieved, defaults to 1. Use -1 for the
            entire subtree or provide an integer larger than 0.
    pierce: Optional[bool]
            Whether or not iframes and shadow roots should be traversed when returning the subtree
            (default is false).

    Returns
    -------
    node: Node
            Node description.
    """
    response = yield {
        "method": "DOM.describeNode",
        "params": filter_none(
            {
                "nodeId": int(nodeId) if nodeId else None,
                "backendNodeId": int(backendNodeId) if backendNodeId else None,
                "objectId": str(objectId) if objectId else None,
                "depth": depth,
                "pierce": pierce,
            }
        ),
    }
    return Node.from_json(response["node"])


def scroll_into_view_if_needed(
    nodeId: Optional[NodeId] = None,
    backendNodeId: Optional[BackendNodeId] = None,
    objectId: Optional[runtime.RemoteObjectId] = None,
    rect: Optional[Rect] = None,
) -> dict:
    """Scrolls the specified rect of the given node into view if not already visible.
    Note: exactly one between nodeId, backendNodeId and objectId should be passed
    to identify the node.

    Parameters
    ----------
    nodeId: Optional[NodeId]
            Identifier of the node.
    backendNodeId: Optional[BackendNodeId]
            Identifier of the backend node.
    objectId: Optional[runtime.RemoteObjectId]
            JavaScript object id of the node wrapper.
    rect: Optional[Rect]
            The rect to be scrolled into view, relative to the node's border box, in CSS pixels.
            When omitted, center of the node will be used, similar to Element.scrollIntoView.

    **Experimental**
    """
    return {
        "method": "DOM.scrollIntoViewIfNeeded",
        "params": filter_none(
            {
                "nodeId": int(nodeId) if nodeId else None,
                "backendNodeId": int(backendNodeId) if backendNodeId else None,
                "objectId": str(objectId) if objectId else None,
                "rect": rect.to_json() if rect else None,
            }
        ),
    }


def disable() -> dict:
    """Disables DOM agent for the given page."""
    return {"method": "DOM.disable", "params": {}}


def discard_search_results(searchId: str) -> dict:
    """Discards search results from the session with the given id. `getSearchResults` should no longer
    be called for that search.

    Parameters
    ----------
    searchId: str
            Unique search session identifier.

    **Experimental**
    """
    return {"method": "DOM.discardSearchResults", "params": {"searchId": searchId}}


def enable() -> dict:
    """Enables DOM agent for the given page."""
    return {"method": "DOM.enable", "params": {}}


def focus(
    nodeId: Optional[NodeId] = None,
    backendNodeId: Optional[BackendNodeId] = None,
    objectId: Optional[runtime.RemoteObjectId] = None,
) -> dict:
    """Focuses the given element.

    Parameters
    ----------
    nodeId: Optional[NodeId]
            Identifier of the node.
    backendNodeId: Optional[BackendNodeId]
            Identifier of the backend node.
    objectId: Optional[runtime.RemoteObjectId]
            JavaScript object id of the node wrapper.
    """
    return {
        "method": "DOM.focus",
        "params": filter_none(
            {
                "nodeId": int(nodeId) if nodeId else None,
                "backendNodeId": int(backendNodeId) if backendNodeId else None,
                "objectId": str(objectId) if objectId else None,
            }
        ),
    }


def get_attributes(nodeId: NodeId) -> Generator[dict, dict, list[str]]:
    """Returns attributes for the specified node.

    Parameters
    ----------
    nodeId: NodeId
            Id of the node to retrieve attibutes for.

    Returns
    -------
    attributes: list[str]
            An interleaved array of node attribute names and values.
    """
    response = yield {"method": "DOM.getAttributes", "params": {"nodeId": int(nodeId)}}
    return response["attributes"]


def get_box_model(
    nodeId: Optional[NodeId] = None,
    backendNodeId: Optional[BackendNodeId] = None,
    objectId: Optional[runtime.RemoteObjectId] = None,
) -> Generator[dict, dict, BoxModel]:
    """Returns boxes for the given node.

    Parameters
    ----------
    nodeId: Optional[NodeId]
            Identifier of the node.
    backendNodeId: Optional[BackendNodeId]
            Identifier of the backend node.
    objectId: Optional[runtime.RemoteObjectId]
            JavaScript object id of the node wrapper.

    Returns
    -------
    model: BoxModel
            Box model for the node.
    """
    response = yield {
        "method": "DOM.getBoxModel",
        "params": filter_none(
            {
                "nodeId": int(nodeId) if nodeId else None,
                "backendNodeId": int(backendNodeId) if backendNodeId else None,
                "objectId": str(objectId) if objectId else None,
            }
        ),
    }
    return BoxModel.from_json(response["model"])


def get_content_quads(
    nodeId: Optional[NodeId] = None,
    backendNodeId: Optional[BackendNodeId] = None,
    objectId: Optional[runtime.RemoteObjectId] = None,
) -> Generator[dict, dict, list[Quad]]:
    """Returns quads that describe node position on the page. This method
    might return multiple quads for inline nodes.

    Parameters
    ----------
    nodeId: Optional[NodeId]
            Identifier of the node.
    backendNodeId: Optional[BackendNodeId]
            Identifier of the backend node.
    objectId: Optional[runtime.RemoteObjectId]
            JavaScript object id of the node wrapper.

    Returns
    -------
    quads: list[Quad]
            Quads that describe node layout relative to viewport.

    **Experimental**
    """
    response = yield {
        "method": "DOM.getContentQuads",
        "params": filter_none(
            {
                "nodeId": int(nodeId) if nodeId else None,
                "backendNodeId": int(backendNodeId) if backendNodeId else None,
                "objectId": str(objectId) if objectId else None,
            }
        ),
    }
    return [Quad(q) for q in response["quads"]]


def get_document(
    depth: Optional[int] = None, pierce: Optional[bool] = None
) -> Generator[dict, dict, Node]:
    """Returns the root DOM node (and optionally the subtree) to the caller.

    Parameters
    ----------
    depth: Optional[int]
            The maximum depth at which children should be retrieved, defaults to 1. Use -1 for the
            entire subtree or provide an integer larger than 0.
    pierce: Optional[bool]
            Whether or not iframes and shadow roots should be traversed when returning the subtree
            (default is false).

    Returns
    -------
    root: Node
            Resulting node.
    """
    response = yield {
        "method": "DOM.getDocument",
        "params": filter_none({"depth": depth, "pierce": pierce}),
    }
    return Node.from_json(response["root"])


@deprecated(version=1.3)
def get_flattened_document(
    depth: Optional[int] = None, pierce: Optional[bool] = None
) -> Generator[dict, dict, list[Node]]:
    """Returns the root DOM node (and optionally the subtree) to the caller.
    Deprecated, as it is not designed to work well with the rest of the DOM agent.
    Use DOMSnapshot.captureSnapshot instead.

    Parameters
    ----------
    depth: Optional[int]
            The maximum depth at which children should be retrieved, defaults to 1. Use -1 for the
            entire subtree or provide an integer larger than 0.
    pierce: Optional[bool]
            Whether or not iframes and shadow roots should be traversed when returning the subtree
            (default is false).

    Returns
    -------
    nodes: list[Node]
            Resulting node.
    """
    response = yield {
        "method": "DOM.getFlattenedDocument",
        "params": filter_none({"depth": depth, "pierce": pierce}),
    }
    return [Node.from_json(n) for n in response["nodes"]]


def get_nodes_for_subtree_by_style(
    nodeId: NodeId,
    computedStyles: list[CSSComputedStyleProperty],
    pierce: Optional[bool] = None,
) -> Generator[dict, dict, list[NodeId]]:
    """Finds nodes with a given computed style in a subtree.

    Parameters
    ----------
    nodeId: NodeId
            Node ID pointing to the root of a subtree.
    computedStyles: list[CSSComputedStyleProperty]
            The style to filter nodes by (includes nodes if any of properties matches).
    pierce: Optional[bool]
            Whether or not iframes and shadow roots in the same target should be traversed when returning the
            results (default is false).

    Returns
    -------
    nodeIds: list[NodeId]
            Resulting nodes.

    **Experimental**
    """
    response = yield {
        "method": "DOM.getNodesForSubtreeByStyle",
        "params": filter_none(
            {
                "nodeId": int(nodeId),
                "computedStyles": [c.to_json() for c in computedStyles],
                "pierce": pierce,
            }
        ),
    }
    return [NodeId(n) for n in response["nodeIds"]]


def get_node_for_location(
    x: int,
    y: int,
    includeUserAgentShadowDOM: Optional[bool] = None,
    ignorePointerEventsNone: Optional[bool] = None,
) -> Generator[dict, dict, dict]:
    """Returns node id at given location. Depending on whether DOM domain is enabled, nodeId is
    either returned or not.

    Parameters
    ----------
    x: int
            X coordinate.
    y: int
            Y coordinate.
    includeUserAgentShadowDOM: Optional[bool]
            False to skip to the nearest non-UA shadow root ancestor (default: false).
    ignorePointerEventsNone: Optional[bool]
            Whether to ignore pointer-events: none on elements and hit test them.

    Returns
    -------
    backendNodeId: BackendNodeId
            Resulting node.
    frameId: page.FrameId
            Frame this node belongs to.
    nodeId: Optional[NodeId]
            Id of the node at given coordinates, only when enabled and requested document.
    """
    response = yield {
        "method": "DOM.getNodeForLocation",
        "params": filter_none(
            {
                "x": x,
                "y": y,
                "includeUserAgentShadowDOM": includeUserAgentShadowDOM,
                "ignorePointerEventsNone": ignorePointerEventsNone,
            }
        ),
    }
    return {
        "backendNodeId": BackendNodeId(response["backendNodeId"]),
        "frameId": page.FrameId(response["frameId"]),
        "nodeId": NodeId(response["nodeId"]) if "nodeId" in response else None,
    }


def get_outer_html(
    nodeId: Optional[NodeId] = None,
    backendNodeId: Optional[BackendNodeId] = None,
    objectId: Optional[runtime.RemoteObjectId] = None,
) -> Generator[dict, dict, str]:
    """Returns node's HTML markup.

    Parameters
    ----------
    nodeId: Optional[NodeId]
            Identifier of the node.
    backendNodeId: Optional[BackendNodeId]
            Identifier of the backend node.
    objectId: Optional[runtime.RemoteObjectId]
            JavaScript object id of the node wrapper.

    Returns
    -------
    outerHTML: str
            Outer HTML markup.
    """
    response = yield {
        "method": "DOM.getOuterHTML",
        "params": filter_none(
            {
                "nodeId": int(nodeId) if nodeId else None,
                "backendNodeId": int(backendNodeId) if backendNodeId else None,
                "objectId": str(objectId) if objectId else None,
            }
        ),
    }
    return response["outerHTML"]


def get_relayout_boundary(nodeId: NodeId) -> Generator[dict, dict, NodeId]:
    """Returns the id of the nearest ancestor that is a relayout boundary.

    Parameters
    ----------
    nodeId: NodeId
            Id of the node.

    Returns
    -------
    nodeId: NodeId
            Relayout boundary node id for the given node.

    **Experimental**
    """
    response = yield {
        "method": "DOM.getRelayoutBoundary",
        "params": {"nodeId": int(nodeId)},
    }
    return NodeId(response["nodeId"])


def get_search_results(
    searchId: str, fromIndex: int, toIndex: int
) -> Generator[dict, dict, list[NodeId]]:
    """Returns search results from given `fromIndex` to given `toIndex` from the search with the given
    identifier.

    Parameters
    ----------
    searchId: str
            Unique search session identifier.
    fromIndex: int
            Start index of the search result to be returned.
    toIndex: int
            End index of the search result to be returned.

    Returns
    -------
    nodeIds: list[NodeId]
            Ids of the search result nodes.

    **Experimental**
    """
    response = yield {
        "method": "DOM.getSearchResults",
        "params": {"searchId": searchId, "fromIndex": fromIndex, "toIndex": toIndex},
    }
    return [NodeId(n) for n in response["nodeIds"]]


def hide_highlight() -> dict:
    """Hides any highlight."""
    return {"method": "DOM.hideHighlight", "params": {}}


def highlight_node() -> dict:
    """Highlights DOM node."""
    return {"method": "DOM.highlightNode", "params": {}}


def highlight_rect() -> dict:
    """Highlights given rectangle."""
    return {"method": "DOM.highlightRect", "params": {}}


def mark_undoable_state() -> dict:
    """Marks last undoable state.

    **Experimental**
    """
    return {"method": "DOM.markUndoableState", "params": {}}


def move_to(
    nodeId: NodeId, targetNodeId: NodeId, insertBeforeNodeId: Optional[NodeId] = None
) -> Generator[dict, dict, NodeId]:
    """Moves node into the new container, places it before the given anchor.

    Parameters
    ----------
    nodeId: NodeId
            Id of the node to move.
    targetNodeId: NodeId
            Id of the element to drop the moved node into.
    insertBeforeNodeId: Optional[NodeId]
            Drop node before this one (if absent, the moved node becomes the last child of
            `targetNodeId`).

    Returns
    -------
    nodeId: NodeId
            New id of the moved node.
    """
    response = yield {
        "method": "DOM.moveTo",
        "params": filter_none(
            {
                "nodeId": int(nodeId),
                "targetNodeId": int(targetNodeId),
                "insertBeforeNodeId": int(insertBeforeNodeId)
                if insertBeforeNodeId
                else None,
            }
        ),
    }
    return NodeId(response["nodeId"])


def perform_search(
    query: str, includeUserAgentShadowDOM: Optional[bool] = None
) -> Generator[dict, dict, dict]:
    """Searches for a given string in the DOM tree. Use `getSearchResults` to access search results or
    `cancelSearch` to end this search session.

    Parameters
    ----------
    query: str
            Plain text or query selector or XPath search query.
    includeUserAgentShadowDOM: Optional[bool]
            True to search in user agent shadow DOM.

    Returns
    -------
    searchId: str
            Unique search session identifier.
    resultCount: int
            Number of search results.

    **Experimental**
    """
    response = yield {
        "method": "DOM.performSearch",
        "params": filter_none(
            {"query": query, "includeUserAgentShadowDOM": includeUserAgentShadowDOM}
        ),
    }
    return {"searchId": response["searchId"], "resultCount": response["resultCount"]}


def push_node_by_path_to_frontend(path: str) -> Generator[dict, dict, NodeId]:
    """Requests that the node is sent to the caller given its path. // FIXME, use XPath

    Parameters
    ----------
    path: str
            Path to node in the proprietary format.

    Returns
    -------
    nodeId: NodeId
            Id of the node for given path.

    **Experimental**
    """
    response = yield {
        "method": "DOM.pushNodeByPathToFrontend",
        "params": {"path": path},
    }
    return NodeId(response["nodeId"])


def push_nodes_by_backend_ids_to_frontend(
    backendNodeIds: list[BackendNodeId],
) -> Generator[dict, dict, list[NodeId]]:
    """Requests that a batch of nodes is sent to the caller given their backend node ids.

    Parameters
    ----------
    backendNodeIds: list[BackendNodeId]
            The array of backend node ids.

    Returns
    -------
    nodeIds: list[NodeId]
            The array of ids of pushed nodes that correspond to the backend ids specified in
            backendNodeIds.

    **Experimental**
    """
    response = yield {
        "method": "DOM.pushNodesByBackendIdsToFrontend",
        "params": {"backendNodeIds": [int(b) for b in backendNodeIds]},
    }
    return [NodeId(n) for n in response["nodeIds"]]


def query_selector(nodeId: NodeId, selector: str) -> Generator[dict, dict, NodeId]:
    """Executes `querySelector` on a given node.

    Parameters
    ----------
    nodeId: NodeId
            Id of the node to query upon.
    selector: str
            Selector string.

    Returns
    -------
    nodeId: NodeId
            Query selector result.
    """
    response = yield {
        "method": "DOM.querySelector",
        "params": {"nodeId": int(nodeId), "selector": selector},
    }
    return NodeId(response["nodeId"])


def query_selector_all(
    nodeId: NodeId, selector: str
) -> Generator[dict, dict, list[NodeId]]:
    """Executes `querySelectorAll` on a given node.

    Parameters
    ----------
    nodeId: NodeId
            Id of the node to query upon.
    selector: str
            Selector string.

    Returns
    -------
    nodeIds: list[NodeId]
            Query selector result.
    """
    response = yield {
        "method": "DOM.querySelectorAll",
        "params": {"nodeId": int(nodeId), "selector": selector},
    }
    return [NodeId(n) for n in response["nodeIds"]]


def redo() -> dict:
    """Re-does the last undone action.

    **Experimental**
    """
    return {"method": "DOM.redo", "params": {}}


def remove_attribute(nodeId: NodeId, name: str) -> dict:
    """Removes attribute with given name from an element with given id.

    Parameters
    ----------
    nodeId: NodeId
            Id of the element to remove attribute from.
    name: str
            Name of the attribute to remove.
    """
    return {
        "method": "DOM.removeAttribute",
        "params": {"nodeId": int(nodeId), "name": name},
    }


def remove_node(nodeId: NodeId) -> dict:
    """Removes node with given id.

    Parameters
    ----------
    nodeId: NodeId
            Id of the node to remove.
    """
    return {"method": "DOM.removeNode", "params": {"nodeId": int(nodeId)}}


def request_child_nodes(
    nodeId: NodeId, depth: Optional[int] = None, pierce: Optional[bool] = None
) -> dict:
    """Requests that children of the node with given id are returned to the caller in form of
    `setChildNodes` events where not only immediate children are retrieved, but all children down to
    the specified depth.

    Parameters
    ----------
    nodeId: NodeId
            Id of the node to get children for.
    depth: Optional[int]
            The maximum depth at which children should be retrieved, defaults to 1. Use -1 for the
            entire subtree or provide an integer larger than 0.
    pierce: Optional[bool]
            Whether or not iframes and shadow roots should be traversed when returning the sub-tree
            (default is false).
    """
    return {
        "method": "DOM.requestChildNodes",
        "params": filter_none(
            {"nodeId": int(nodeId), "depth": depth, "pierce": pierce}
        ),
    }


def request_node(objectId: runtime.RemoteObjectId) -> Generator[dict, dict, NodeId]:
    """Requests that the node is sent to the caller given the JavaScript node object reference. All
    nodes that form the path from the node to the root are also sent to the client as a series of
    `setChildNodes` notifications.

    Parameters
    ----------
    objectId: runtime.RemoteObjectId
            JavaScript object id to convert into node.

    Returns
    -------
    nodeId: NodeId
            Node id for given object.
    """
    response = yield {
        "method": "DOM.requestNode",
        "params": {"objectId": str(objectId)},
    }
    return NodeId(response["nodeId"])


def resolve_node(
    nodeId: Optional[NodeId] = None,
    backendNodeId: Optional[BackendNodeId] = None,
    objectGroup: Optional[str] = None,
    executionContextId: Optional[runtime.ExecutionContextId] = None,
) -> Generator[dict, dict, runtime.RemoteObject]:
    """Resolves the JavaScript node object for a given NodeId or BackendNodeId.

    Parameters
    ----------
    nodeId: Optional[NodeId]
            Id of the node to resolve.
    backendNodeId: Optional[BackendNodeId]
            Backend identifier of the node to resolve.
    objectGroup: Optional[str]
            Symbolic group name that can be used to release multiple objects.
    executionContextId: Optional[runtime.ExecutionContextId]
            Execution context in which to resolve the node.

    Returns
    -------
    object: runtime.RemoteObject
            JavaScript object wrapper for given node.
    """
    response = yield {
        "method": "DOM.resolveNode",
        "params": filter_none(
            {
                "nodeId": int(nodeId) if nodeId else None,
                "backendNodeId": int(backendNodeId) if backendNodeId else None,
                "objectGroup": objectGroup,
                "executionContextId": int(executionContextId)
                if executionContextId
                else None,
            }
        ),
    }
    return runtime.RemoteObject.from_json(response["object"])


def set_attribute_value(nodeId: NodeId, name: str, value: str) -> dict:
    """Sets attribute for an element with given id.

    Parameters
    ----------
    nodeId: NodeId
            Id of the element to set attribute for.
    name: str
            Attribute name.
    value: str
            Attribute value.
    """
    return {
        "method": "DOM.setAttributeValue",
        "params": {"nodeId": int(nodeId), "name": name, "value": value},
    }


def set_attributes_as_text(
    nodeId: NodeId, text: str, name: Optional[str] = None
) -> dict:
    """Sets attributes on element with given id. This method is useful when user edits some existing
    attribute value and types in several attribute name/value pairs.

    Parameters
    ----------
    nodeId: NodeId
            Id of the element to set attributes for.
    text: str
            Text with a number of attributes. Will parse this text using HTML parser.
    name: Optional[str]
            Attribute name to replace with new attributes derived from text in case text parsed
            successfully.
    """
    return {
        "method": "DOM.setAttributesAsText",
        "params": filter_none({"nodeId": int(nodeId), "text": text, "name": name}),
    }


def set_file_input_files(
    files: list[str],
    nodeId: Optional[NodeId] = None,
    backendNodeId: Optional[BackendNodeId] = None,
    objectId: Optional[runtime.RemoteObjectId] = None,
) -> dict:
    """Sets files for the given file input element.

    Parameters
    ----------
    files: list[str]
            Array of file paths to set.
    nodeId: Optional[NodeId]
            Identifier of the node.
    backendNodeId: Optional[BackendNodeId]
            Identifier of the backend node.
    objectId: Optional[runtime.RemoteObjectId]
            JavaScript object id of the node wrapper.
    """
    return {
        "method": "DOM.setFileInputFiles",
        "params": filter_none(
            {
                "files": files,
                "nodeId": int(nodeId) if nodeId else None,
                "backendNodeId": int(backendNodeId) if backendNodeId else None,
                "objectId": str(objectId) if objectId else None,
            }
        ),
    }


def set_node_stack_traces_enabled(enable: bool) -> dict:
    """Sets if stack traces should be captured for Nodes. See `Node.getNodeStackTraces`. Default is disabled.

    Parameters
    ----------
    enable: bool
            Enable or disable.

    **Experimental**
    """
    return {"method": "DOM.setNodeStackTracesEnabled", "params": {"enable": enable}}


def get_node_stack_traces(
    nodeId: NodeId,
) -> Generator[dict, dict, Optional[runtime.StackTrace]]:
    """Gets stack traces associated with a Node. As of now, only provides stack trace for Node creation.

    Parameters
    ----------
    nodeId: NodeId
            Id of the node to get stack traces for.

    Returns
    -------
    creation: Optional[runtime.StackTrace]
            Creation stack trace, if available.

    **Experimental**
    """
    response = yield {
        "method": "DOM.getNodeStackTraces",
        "params": {"nodeId": int(nodeId)},
    }
    return (
        runtime.StackTrace.from_json(response["creation"])
        if "creation" in response
        else None
    )


def get_file_info(objectId: runtime.RemoteObjectId) -> Generator[dict, dict, str]:
    """Returns file information for the given
    File wrapper.

    Parameters
    ----------
    objectId: runtime.RemoteObjectId
            JavaScript object id of the node wrapper.

    Returns
    -------
    path: str

    **Experimental**
    """
    response = yield {
        "method": "DOM.getFileInfo",
        "params": {"objectId": str(objectId)},
    }
    return response["path"]


def set_inspected_node(nodeId: NodeId) -> dict:
    """Enables console to refer to the node with given id via $x (see Command Line API for more details
    $x functions).

    Parameters
    ----------
    nodeId: NodeId
            DOM node id to be accessible by means of $x command line API.

    **Experimental**
    """
    return {"method": "DOM.setInspectedNode", "params": {"nodeId": int(nodeId)}}


def set_node_name(nodeId: NodeId, name: str) -> Generator[dict, dict, NodeId]:
    """Sets node name for a node with given id.

    Parameters
    ----------
    nodeId: NodeId
            Id of the node to set name for.
    name: str
            New node's name.

    Returns
    -------
    nodeId: NodeId
            New node's id.
    """
    response = yield {
        "method": "DOM.setNodeName",
        "params": {"nodeId": int(nodeId), "name": name},
    }
    return NodeId(response["nodeId"])


def set_node_value(nodeId: NodeId, value: str) -> dict:
    """Sets node value for a node with given id.

    Parameters
    ----------
    nodeId: NodeId
            Id of the node to set value for.
    value: str
            New node's value.
    """
    return {
        "method": "DOM.setNodeValue",
        "params": {"nodeId": int(nodeId), "value": value},
    }


def set_outer_html(nodeId: NodeId, outerHTML: str) -> dict:
    """Sets node HTML markup, returns new node id.

    Parameters
    ----------
    nodeId: NodeId
            Id of the node to set markup for.
    outerHTML: str
            Outer HTML markup to set.
    """
    return {
        "method": "DOM.setOuterHTML",
        "params": {"nodeId": int(nodeId), "outerHTML": outerHTML},
    }


def undo() -> dict:
    """Undoes the last performed action.

    **Experimental**
    """
    return {"method": "DOM.undo", "params": {}}


def get_frame_owner(frameId: page.FrameId) -> Generator[dict, dict, dict]:
    """Returns iframe node that owns iframe with the given domain.

    Parameters
    ----------
    frameId: page.FrameId

    Returns
    -------
    backendNodeId: BackendNodeId
            Resulting node.
    nodeId: Optional[NodeId]
            Id of the node at given coordinates, only when enabled and requested document.

    **Experimental**
    """
    response = yield {
        "method": "DOM.getFrameOwner",
        "params": {"frameId": str(frameId)},
    }
    return {
        "backendNodeId": BackendNodeId(response["backendNodeId"]),
        "nodeId": NodeId(response["nodeId"]) if "nodeId" in response else None,
    }


@dataclasses.dataclass
class AttributeModified:
    """Fired when `Element`'s attribute is modified.

    Attributes
    ----------
    nodeId: NodeId
            Id of the node that has changed.
    name: str
            Attribute name.
    value: str
            Attribute value.
    """

    nodeId: NodeId
    name: str
    value: str

    @classmethod
    def from_json(cls, json: dict) -> AttributeModified:
        return cls(NodeId(json["nodeId"]), json["name"], json["value"])


@dataclasses.dataclass
class AttributeRemoved:
    """Fired when `Element`'s attribute is removed.

    Attributes
    ----------
    nodeId: NodeId
            Id of the node that has changed.
    name: str
            A ttribute name.
    """

    nodeId: NodeId
    name: str

    @classmethod
    def from_json(cls, json: dict) -> AttributeRemoved:
        return cls(NodeId(json["nodeId"]), json["name"])


@dataclasses.dataclass
class CharacterDataModified:
    """Mirrors `DOMCharacterDataModified` event.

    Attributes
    ----------
    nodeId: NodeId
            Id of the node that has changed.
    characterData: str
            New text value.
    """

    nodeId: NodeId
    characterData: str

    @classmethod
    def from_json(cls, json: dict) -> CharacterDataModified:
        return cls(NodeId(json["nodeId"]), json["characterData"])


@dataclasses.dataclass
class ChildNodeCountUpdated:
    """Fired when `Container`'s child node count has changed.

    Attributes
    ----------
    nodeId: NodeId
            Id of the node that has changed.
    childNodeCount: int
            New node count.
    """

    nodeId: NodeId
    childNodeCount: int

    @classmethod
    def from_json(cls, json: dict) -> ChildNodeCountUpdated:
        return cls(NodeId(json["nodeId"]), json["childNodeCount"])


@dataclasses.dataclass
class ChildNodeInserted:
    """Mirrors `DOMNodeInserted` event.

    Attributes
    ----------
    parentNodeId: NodeId
            Id of the node that has changed.
    previousNodeId: NodeId
            If of the previous siblint.
    node: Node
            Inserted node data.
    """

    parentNodeId: NodeId
    previousNodeId: NodeId
    node: Node

    @classmethod
    def from_json(cls, json: dict) -> ChildNodeInserted:
        return cls(
            NodeId(json["parentNodeId"]),
            NodeId(json["previousNodeId"]),
            Node.from_json(json["node"]),
        )


@dataclasses.dataclass
class ChildNodeRemoved:
    """Mirrors `DOMNodeRemoved` event.

    Attributes
    ----------
    parentNodeId: NodeId
            Parent id.
    nodeId: NodeId
            Id of the node that has been removed.
    """

    parentNodeId: NodeId
    nodeId: NodeId

    @classmethod
    def from_json(cls, json: dict) -> ChildNodeRemoved:
        return cls(NodeId(json["parentNodeId"]), NodeId(json["nodeId"]))


@dataclasses.dataclass
class DistributedNodesUpdated:
    """Called when distrubution is changed.

    Attributes
    ----------
    insertionPointId: NodeId
            Insertion point where distrubuted nodes were updated.
    distributedNodes: list[BackendNode]
            Distributed nodes for given insertion point.
    """

    insertionPointId: NodeId
    distributedNodes: list[BackendNode]

    @classmethod
    def from_json(cls, json: dict) -> DistributedNodesUpdated:
        return cls(
            NodeId(json["insertionPointId"]),
            [BackendNode.from_json(d) for d in json["distributedNodes"]],
        )


@dataclasses.dataclass
class DocumentUpdated:
    """Fired when `Document` has been totally updated. Node ids are no longer valid."""

    @classmethod
    def from_json(cls, json: dict) -> DocumentUpdated:
        return cls()


@dataclasses.dataclass
class InlineStyleInvalidated:
    """Fired when `Element`'s inline style is modified via a CSS property modification.

    Attributes
    ----------
    nodeIds: list[NodeId]
            Ids of the nodes for which the inline styles have been invalidated.
    """

    nodeIds: list[NodeId]

    @classmethod
    def from_json(cls, json: dict) -> InlineStyleInvalidated:
        return cls([NodeId(n) for n in json["nodeIds"]])


@dataclasses.dataclass
class PseudoElementAdded:
    """Called when a pseudo element is added to an element.

    Attributes
    ----------
    parentId: NodeId
            Pseudo element's parent element id.
    pseudoElement: Node
            The added pseudo element.
    """

    parentId: NodeId
    pseudoElement: Node

    @classmethod
    def from_json(cls, json: dict) -> PseudoElementAdded:
        return cls(NodeId(json["parentId"]), Node.from_json(json["pseudoElement"]))


@dataclasses.dataclass
class PseudoElementRemoved:
    """Called when a pseudo element is removed from an element.

    Attributes
    ----------
    parentId: NodeId
            Pseudo element's parent element id.
    pseudoElementId: NodeId
            The removed pseudo element id.
    """

    parentId: NodeId
    pseudoElementId: NodeId

    @classmethod
    def from_json(cls, json: dict) -> PseudoElementRemoved:
        return cls(NodeId(json["parentId"]), NodeId(json["pseudoElementId"]))


@dataclasses.dataclass
class SetChildNodes:
    """Fired when backend wants to provide client with the missing DOM structure. This happens upon
    most of the calls requesting node ids.

    Attributes
    ----------
    parentId: NodeId
            Parent node id to populate with children.
    nodes: list[Node]
            Child nodes array.
    """

    parentId: NodeId
    nodes: list[Node]

    @classmethod
    def from_json(cls, json: dict) -> SetChildNodes:
        return cls(NodeId(json["parentId"]), [Node.from_json(n) for n in json["nodes"]])


@dataclasses.dataclass
class ShadowRootPopped:
    """Called when shadow root is popped from the element.

    Attributes
    ----------
    hostId: NodeId
            Host element id.
    rootId: NodeId
            Shadow root id.
    """

    hostId: NodeId
    rootId: NodeId

    @classmethod
    def from_json(cls, json: dict) -> ShadowRootPopped:
        return cls(NodeId(json["hostId"]), NodeId(json["rootId"]))


@dataclasses.dataclass
class ShadowRootPushed:
    """Called when shadow root is pushed into the element.

    Attributes
    ----------
    hostId: NodeId
            Host element id.
    root: Node
            Shadow root.
    """

    hostId: NodeId
    root: Node

    @classmethod
    def from_json(cls, json: dict) -> ShadowRootPushed:
        return cls(NodeId(json["hostId"]), Node.from_json(json["root"]))
