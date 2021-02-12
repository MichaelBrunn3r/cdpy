from __future__ import annotations

import dataclasses
from typing import Optional

from . import dom, dom_debugger, page
from .common import filter_none, filter_unset_parameters


@dataclasses.dataclass
class DOMNode:
    """A Node in the DOM tree.

    Attributes
    ----------
    nodeType: int
            `Node`'s nodeType.
    nodeName: str
            `Node`'s nodeName.
    nodeValue: str
            `Node`'s nodeValue.
    backendNodeId: dom.BackendNodeId
            `Node`'s id, corresponds to DOM.Node.backendNodeId.
    textValue: Optional[str]
            Only set for textarea elements, contains the text value.
    inputValue: Optional[str]
            Only set for input elements, contains the input's associated text value.
    inputChecked: Optional[bool]
            Only set for radio and checkbox input elements, indicates if the element has been checked
    optionSelected: Optional[bool]
            Only set for option elements, indicates if the element has been selected
    childNodeIndexes: Optional[list[int]]
            The indexes of the node's child nodes in the `domNodes` array returned by `getSnapshot`, if
            any.
    attributes: Optional[list[NameValue]]
            Attributes of an `Element` node.
    pseudoElementIndexes: Optional[list[int]]
            Indexes of pseudo elements associated with this node in the `domNodes` array returned by
            `getSnapshot`, if any.
    layoutNodeIndex: Optional[int]
            The index of the node's related layout tree node in the `layoutTreeNodes` array returned by
            `getSnapshot`, if any.
    documentURL: Optional[str]
            Document URL that `Document` or `FrameOwner` node points to.
    baseURL: Optional[str]
            Base URL that `Document` or `FrameOwner` node uses for URL completion.
    contentLanguage: Optional[str]
            Only set for documents, contains the document's content language.
    documentEncoding: Optional[str]
            Only set for documents, contains the document's character set encoding.
    publicId: Optional[str]
            `DocumentType` node's publicId.
    systemId: Optional[str]
            `DocumentType` node's systemId.
    frameId: Optional[page.FrameId]
            Frame ID for frame owner elements and also for the document node.
    contentDocumentIndex: Optional[int]
            The index of a frame owner element's content document in the `domNodes` array returned by
            `getSnapshot`, if any.
    pseudoType: Optional[dom.PseudoType]
            Type of a pseudo element node.
    shadowRootType: Optional[dom.ShadowRootType]
            Shadow root type.
    isClickable: Optional[bool]
            Whether this DOM node responds to mouse clicks. This includes nodes that have had click
            event listeners attached via JavaScript as well as anchor tags that naturally navigate when
            clicked.
    eventListeners: Optional[list[dom_debugger.EventListener]]
            Details of the node's event listeners, if any.
    currentSourceURL: Optional[str]
            The selected url for nodes with a srcset attribute.
    originURL: Optional[str]
            The url of the script (if any) that generates this node.
    scrollOffsetX: Optional[float]
            Scroll offsets, set when this node is a Document.
    scrollOffsetY: Optional[float]
    """

    nodeType: int
    nodeName: str
    nodeValue: str
    backendNodeId: dom.BackendNodeId
    textValue: Optional[str] = None
    inputValue: Optional[str] = None
    inputChecked: Optional[bool] = None
    optionSelected: Optional[bool] = None
    childNodeIndexes: Optional[list[int]] = None
    attributes: Optional[list[NameValue]] = None
    pseudoElementIndexes: Optional[list[int]] = None
    layoutNodeIndex: Optional[int] = None
    documentURL: Optional[str] = None
    baseURL: Optional[str] = None
    contentLanguage: Optional[str] = None
    documentEncoding: Optional[str] = None
    publicId: Optional[str] = None
    systemId: Optional[str] = None
    frameId: Optional[page.FrameId] = None
    contentDocumentIndex: Optional[int] = None
    pseudoType: Optional[dom.PseudoType] = None
    shadowRootType: Optional[dom.ShadowRootType] = None
    isClickable: Optional[bool] = None
    eventListeners: Optional[list[dom_debugger.EventListener]] = None
    currentSourceURL: Optional[str] = None
    originURL: Optional[str] = None
    scrollOffsetX: Optional[float] = None
    scrollOffsetY: Optional[float] = None

    @classmethod
    def from_json(cls, json: dict) -> DOMNode:
        return cls(
            json["nodeType"],
            json["nodeName"],
            json["nodeValue"],
            dom.BackendNodeId(json["backendNodeId"]),
            json.get("textValue"),
            json.get("inputValue"),
            json.get("inputChecked"),
            json.get("optionSelected"),
            json.get("childNodeIndexes"),
            [NameValue.from_json(a) for a in json["attributes"]]
            if "attributes" in json
            else None,
            json.get("pseudoElementIndexes"),
            json.get("layoutNodeIndex"),
            json.get("documentURL"),
            json.get("baseURL"),
            json.get("contentLanguage"),
            json.get("documentEncoding"),
            json.get("publicId"),
            json.get("systemId"),
            page.FrameId(json["frameId"]) if "frameId" in json else None,
            json.get("contentDocumentIndex"),
            dom.PseudoType(json["pseudoType"]) if "pseudoType" in json else None,
            dom.ShadowRootType(json["shadowRootType"])
            if "shadowRootType" in json
            else None,
            json.get("isClickable"),
            [dom_debugger.EventListener.from_json(e) for e in json["eventListeners"]]
            if "eventListeners" in json
            else None,
            json.get("currentSourceURL"),
            json.get("originURL"),
            json.get("scrollOffsetX"),
            json.get("scrollOffsetY"),
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "nodeType": self.nodeType,
                "nodeName": self.nodeName,
                "nodeValue": self.nodeValue,
                "backendNodeId": int(self.backendNodeId),
                "textValue": self.textValue,
                "inputValue": self.inputValue,
                "inputChecked": self.inputChecked,
                "optionSelected": self.optionSelected,
                "childNodeIndexes": self.childNodeIndexes,
                "attributes": [a.to_json() for a in self.attributes]
                if self.attributes
                else None,
                "pseudoElementIndexes": self.pseudoElementIndexes,
                "layoutNodeIndex": self.layoutNodeIndex,
                "documentURL": self.documentURL,
                "baseURL": self.baseURL,
                "contentLanguage": self.contentLanguage,
                "documentEncoding": self.documentEncoding,
                "publicId": self.publicId,
                "systemId": self.systemId,
                "frameId": str(self.frameId) if self.frameId else None,
                "contentDocumentIndex": self.contentDocumentIndex,
                "pseudoType": self.pseudoType.value if self.pseudoType else None,
                "shadowRootType": self.shadowRootType.value
                if self.shadowRootType
                else None,
                "isClickable": self.isClickable,
                "eventListeners": [e.to_json() for e in self.eventListeners]
                if self.eventListeners
                else None,
                "currentSourceURL": self.currentSourceURL,
                "originURL": self.originURL,
                "scrollOffsetX": self.scrollOffsetX,
                "scrollOffsetY": self.scrollOffsetY,
            }
        )


@dataclasses.dataclass
class InlineTextBox:
    """Details of post layout rendered text positions. The exact layout should not be regarded as
    stable and may change between versions.

    Attributes
    ----------
    boundingBox: dom.Rect
            The bounding box in document coordinates. Note that scroll offset of the document is ignored.
    startCharacterIndex: int
            The starting index in characters, for this post layout textbox substring. Characters that
            would be represented as a surrogate pair in UTF-16 have length 2.
    numCharacters: int
            The number of characters in this post layout textbox substring. Characters that would be
            represented as a surrogate pair in UTF-16 have length 2.
    """

    boundingBox: dom.Rect
    startCharacterIndex: int
    numCharacters: int

    @classmethod
    def from_json(cls, json: dict) -> InlineTextBox:
        return cls(
            dom.Rect.from_json(json["boundingBox"]),
            json["startCharacterIndex"],
            json["numCharacters"],
        )

    def to_json(self) -> dict:
        return {
            "boundingBox": self.boundingBox.to_json(),
            "startCharacterIndex": self.startCharacterIndex,
            "numCharacters": self.numCharacters,
        }


@dataclasses.dataclass
class LayoutTreeNode:
    """Details of an element in the DOM tree with a LayoutObject.

    Attributes
    ----------
    domNodeIndex: int
            The index of the related DOM node in the `domNodes` array returned by `getSnapshot`.
    boundingBox: dom.Rect
            The bounding box in document coordinates. Note that scroll offset of the document is ignored.
    layoutText: Optional[str]
            Contents of the LayoutText, if any.
    inlineTextNodes: Optional[list[InlineTextBox]]
            The post-layout inline text nodes, if any.
    styleIndex: Optional[int]
            Index into the `computedStyles` array returned by `getSnapshot`.
    paintOrder: Optional[int]
            Global paint order index, which is determined by the stacking order of the nodes. Nodes
            that are painted together will have the same index. Only provided if includePaintOrder in
            getSnapshot was true.
    isStackingContext: Optional[bool]
            Set to true to indicate the element begins a new stacking context.
    """

    domNodeIndex: int
    boundingBox: dom.Rect
    layoutText: Optional[str] = None
    inlineTextNodes: Optional[list[InlineTextBox]] = None
    styleIndex: Optional[int] = None
    paintOrder: Optional[int] = None
    isStackingContext: Optional[bool] = None

    @classmethod
    def from_json(cls, json: dict) -> LayoutTreeNode:
        return cls(
            json["domNodeIndex"],
            dom.Rect.from_json(json["boundingBox"]),
            json.get("layoutText"),
            [InlineTextBox.from_json(i) for i in json["inlineTextNodes"]]
            if "inlineTextNodes" in json
            else None,
            json.get("styleIndex"),
            json.get("paintOrder"),
            json.get("isStackingContext"),
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "domNodeIndex": self.domNodeIndex,
                "boundingBox": self.boundingBox.to_json(),
                "layoutText": self.layoutText,
                "inlineTextNodes": [i.to_json() for i in self.inlineTextNodes]
                if self.inlineTextNodes
                else None,
                "styleIndex": self.styleIndex,
                "paintOrder": self.paintOrder,
                "isStackingContext": self.isStackingContext,
            }
        )


@dataclasses.dataclass
class ComputedStyle:
    """A subset of the full ComputedStyle as defined by the request whitelist.

    Attributes
    ----------
    properties: list[NameValue]
            Name/value pairs of computed style properties.
    """

    properties: list[NameValue]

    @classmethod
    def from_json(cls, json: dict) -> ComputedStyle:
        return cls([NameValue.from_json(p) for p in json["properties"]])

    def to_json(self) -> dict:
        return {"properties": [p.to_json() for p in self.properties]}


@dataclasses.dataclass
class NameValue:
    """A name/value pair.

    Attributes
    ----------
    name: str
            Attribute/property name.
    value: str
            Attribute/property value.
    """

    name: str
    value: str

    @classmethod
    def from_json(cls, json: dict) -> NameValue:
        return cls(json["name"], json["value"])

    def to_json(self) -> dict:
        return {"name": self.name, "value": self.value}


class StringIndex(int):
    """Index of the string in the strings table."""

    def __repr__(self):
        return f"StringIndex({super().__repr__()})"


class ArrayOfStrings(list[StringIndex]):
    """Index of the string in the strings table."""

    @classmethod
    def from_json(cls, json: dict) -> ArrayOfStrings:
        return cls([StringIndex(e) for e in json])

    def to_json(self) -> dict:
        return [int(e) for e in self]


@dataclasses.dataclass
class RareStringData:
    """Data that is only present on rare nodes.

    Attributes
    ----------
    index: list[int]
    value: list[StringIndex]
    """

    index: list[int]
    value: list[StringIndex]

    @classmethod
    def from_json(cls, json: dict) -> RareStringData:
        return cls(json["index"], [StringIndex(v) for v in json["value"]])

    def to_json(self) -> dict:
        return {"index": self.index, "value": [int(v) for v in self.value]}


@dataclasses.dataclass
class RareBooleanData:
    """
    Attributes
    ----------
    index: list[int]
    """

    index: list[int]

    @classmethod
    def from_json(cls, json: dict) -> RareBooleanData:
        return cls(json["index"])

    def to_json(self) -> dict:
        return {"index": self.index}


@dataclasses.dataclass
class RareIntegerData:
    """
    Attributes
    ----------
    index: list[int]
    value: list[int]
    """

    index: list[int]
    value: list[int]

    @classmethod
    def from_json(cls, json: dict) -> RareIntegerData:
        return cls(json["index"], json["value"])

    def to_json(self) -> dict:
        return {"index": self.index, "value": self.value}


class Rectangle(list[float]):
    """"""

    def __repr__(self):
        return f"Rectangle({super().__repr__()})"


@dataclasses.dataclass
class DocumentSnapshot:
    """Document snapshot.

    Attributes
    ----------
    documentURL: StringIndex
            Document URL that `Document` or `FrameOwner` node points to.
    title: StringIndex
            Document title.
    baseURL: StringIndex
            Base URL that `Document` or `FrameOwner` node uses for URL completion.
    contentLanguage: StringIndex
            Contains the document's content language.
    encodingName: StringIndex
            Contains the document's character set encoding.
    publicId: StringIndex
            `DocumentType` node's publicId.
    systemId: StringIndex
            `DocumentType` node's systemId.
    frameId: StringIndex
            Frame ID for frame owner elements and also for the document node.
    nodes: NodeTreeSnapshot
            A table with dom nodes.
    layout: LayoutTreeSnapshot
            The nodes in the layout tree.
    textBoxes: TextBoxSnapshot
            The post-layout inline text nodes.
    scrollOffsetX: Optional[float]
            Horizontal scroll offset.
    scrollOffsetY: Optional[float]
            Vertical scroll offset.
    contentWidth: Optional[float]
            Document content width.
    contentHeight: Optional[float]
            Document content height.
    """

    documentURL: StringIndex
    title: StringIndex
    baseURL: StringIndex
    contentLanguage: StringIndex
    encodingName: StringIndex
    publicId: StringIndex
    systemId: StringIndex
    frameId: StringIndex
    nodes: NodeTreeSnapshot
    layout: LayoutTreeSnapshot
    textBoxes: TextBoxSnapshot
    scrollOffsetX: Optional[float] = None
    scrollOffsetY: Optional[float] = None
    contentWidth: Optional[float] = None
    contentHeight: Optional[float] = None

    @classmethod
    def from_json(cls, json: dict) -> DocumentSnapshot:
        return cls(
            StringIndex(json["documentURL"]),
            StringIndex(json["title"]),
            StringIndex(json["baseURL"]),
            StringIndex(json["contentLanguage"]),
            StringIndex(json["encodingName"]),
            StringIndex(json["publicId"]),
            StringIndex(json["systemId"]),
            StringIndex(json["frameId"]),
            NodeTreeSnapshot.from_json(json["nodes"]),
            LayoutTreeSnapshot.from_json(json["layout"]),
            TextBoxSnapshot.from_json(json["textBoxes"]),
            json.get("scrollOffsetX"),
            json.get("scrollOffsetY"),
            json.get("contentWidth"),
            json.get("contentHeight"),
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "documentURL": int(self.documentURL),
                "title": int(self.title),
                "baseURL": int(self.baseURL),
                "contentLanguage": int(self.contentLanguage),
                "encodingName": int(self.encodingName),
                "publicId": int(self.publicId),
                "systemId": int(self.systemId),
                "frameId": int(self.frameId),
                "nodes": self.nodes.to_json(),
                "layout": self.layout.to_json(),
                "textBoxes": self.textBoxes.to_json(),
                "scrollOffsetX": self.scrollOffsetX,
                "scrollOffsetY": self.scrollOffsetY,
                "contentWidth": self.contentWidth,
                "contentHeight": self.contentHeight,
            }
        )


@dataclasses.dataclass
class NodeTreeSnapshot:
    """Table containing nodes.

    Attributes
    ----------
    parentIndex: Optional[list[int]]
            Parent node index.
    nodeType: Optional[list[int]]
            `Node`'s nodeType.
    nodeName: Optional[list[StringIndex]]
            `Node`'s nodeName.
    nodeValue: Optional[list[StringIndex]]
            `Node`'s nodeValue.
    backendNodeId: Optional[list[dom.BackendNodeId]]
            `Node`'s id, corresponds to DOM.Node.backendNodeId.
    attributes: Optional[list[ArrayOfStrings]]
            Attributes of an `Element` node. Flatten name, value pairs.
    textValue: Optional[RareStringData]
            Only set for textarea elements, contains the text value.
    inputValue: Optional[RareStringData]
            Only set for input elements, contains the input's associated text value.
    inputChecked: Optional[RareBooleanData]
            Only set for radio and checkbox input elements, indicates if the element has been checked
    optionSelected: Optional[RareBooleanData]
            Only set for option elements, indicates if the element has been selected
    contentDocumentIndex: Optional[RareIntegerData]
            The index of the document in the list of the snapshot documents.
    pseudoType: Optional[RareStringData]
            Type of a pseudo element node.
    isClickable: Optional[RareBooleanData]
            Whether this DOM node responds to mouse clicks. This includes nodes that have had click
            event listeners attached via JavaScript as well as anchor tags that naturally navigate when
            clicked.
    currentSourceURL: Optional[RareStringData]
            The selected url for nodes with a srcset attribute.
    originURL: Optional[RareStringData]
            The url of the script (if any) that generates this node.
    """

    parentIndex: Optional[list[int]] = None
    nodeType: Optional[list[int]] = None
    nodeName: Optional[list[StringIndex]] = None
    nodeValue: Optional[list[StringIndex]] = None
    backendNodeId: Optional[list[dom.BackendNodeId]] = None
    attributes: Optional[list[ArrayOfStrings]] = None
    textValue: Optional[RareStringData] = None
    inputValue: Optional[RareStringData] = None
    inputChecked: Optional[RareBooleanData] = None
    optionSelected: Optional[RareBooleanData] = None
    contentDocumentIndex: Optional[RareIntegerData] = None
    pseudoType: Optional[RareStringData] = None
    isClickable: Optional[RareBooleanData] = None
    currentSourceURL: Optional[RareStringData] = None
    originURL: Optional[RareStringData] = None

    @classmethod
    def from_json(cls, json: dict) -> NodeTreeSnapshot:
        return cls(
            json.get("parentIndex"),
            json.get("nodeType"),
            [StringIndex(n) for n in json["nodeName"]] if "nodeName" in json else None,
            [StringIndex(n) for n in json["nodeValue"]]
            if "nodeValue" in json
            else None,
            [dom.BackendNodeId(b) for b in json["backendNodeId"]]
            if "backendNodeId" in json
            else None,
            [ArrayOfStrings.from_json(a) for a in json["attributes"]]
            if "attributes" in json
            else None,
            RareStringData.from_json(json["textValue"])
            if "textValue" in json
            else None,
            RareStringData.from_json(json["inputValue"])
            if "inputValue" in json
            else None,
            RareBooleanData.from_json(json["inputChecked"])
            if "inputChecked" in json
            else None,
            RareBooleanData.from_json(json["optionSelected"])
            if "optionSelected" in json
            else None,
            RareIntegerData.from_json(json["contentDocumentIndex"])
            if "contentDocumentIndex" in json
            else None,
            RareStringData.from_json(json["pseudoType"])
            if "pseudoType" in json
            else None,
            RareBooleanData.from_json(json["isClickable"])
            if "isClickable" in json
            else None,
            RareStringData.from_json(json["currentSourceURL"])
            if "currentSourceURL" in json
            else None,
            RareStringData.from_json(json["originURL"])
            if "originURL" in json
            else None,
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "parentIndex": self.parentIndex,
                "nodeType": self.nodeType,
                "nodeName": [int(n) for n in self.nodeName] if self.nodeName else None,
                "nodeValue": [int(n) for n in self.nodeValue]
                if self.nodeValue
                else None,
                "backendNodeId": [int(b) for b in self.backendNodeId]
                if self.backendNodeId
                else None,
                "attributes": [a.to_json() for a in self.attributes]
                if self.attributes
                else None,
                "textValue": self.textValue.to_json() if self.textValue else None,
                "inputValue": self.inputValue.to_json() if self.inputValue else None,
                "inputChecked": self.inputChecked.to_json()
                if self.inputChecked
                else None,
                "optionSelected": self.optionSelected.to_json()
                if self.optionSelected
                else None,
                "contentDocumentIndex": self.contentDocumentIndex.to_json()
                if self.contentDocumentIndex
                else None,
                "pseudoType": self.pseudoType.to_json() if self.pseudoType else None,
                "isClickable": self.isClickable.to_json() if self.isClickable else None,
                "currentSourceURL": self.currentSourceURL.to_json()
                if self.currentSourceURL
                else None,
                "originURL": self.originURL.to_json() if self.originURL else None,
            }
        )


@dataclasses.dataclass
class LayoutTreeSnapshot:
    """Table of details of an element in the DOM tree with a LayoutObject.

    Attributes
    ----------
    nodeIndex: list[int]
            Index of the corresponding node in the `NodeTreeSnapshot` array returned by `captureSnapshot`.
    styles: list[ArrayOfStrings]
            Array of indexes specifying computed style strings, filtered according to the `computedStyles` parameter passed to `captureSnapshot`.
    bounds: list[Rectangle]
            The absolute position bounding box.
    text: list[StringIndex]
            Contents of the LayoutText, if any.
    stackingContexts: RareBooleanData
            Stacking context information.
    paintOrders: Optional[list[int]]
            Global paint order index, which is determined by the stacking order of the nodes. Nodes
            that are painted together will have the same index. Only provided if includePaintOrder in
            captureSnapshot was true.
    offsetRects: Optional[list[Rectangle]]
            The offset rect of nodes. Only available when includeDOMRects is set to true
    scrollRects: Optional[list[Rectangle]]
            The scroll rect of nodes. Only available when includeDOMRects is set to true
    clientRects: Optional[list[Rectangle]]
            The client rect of nodes. Only available when includeDOMRects is set to true
    """

    nodeIndex: list[int]
    styles: list[ArrayOfStrings]
    bounds: list[Rectangle]
    text: list[StringIndex]
    stackingContexts: RareBooleanData
    paintOrders: Optional[list[int]] = None
    offsetRects: Optional[list[Rectangle]] = None
    scrollRects: Optional[list[Rectangle]] = None
    clientRects: Optional[list[Rectangle]] = None

    @classmethod
    def from_json(cls, json: dict) -> LayoutTreeSnapshot:
        return cls(
            json["nodeIndex"],
            [ArrayOfStrings.from_json(s) for s in json["styles"]],
            [Rectangle(b) for b in json["bounds"]],
            [StringIndex(t) for t in json["text"]],
            RareBooleanData.from_json(json["stackingContexts"]),
            json.get("paintOrders"),
            [Rectangle(o) for o in json["offsetRects"]]
            if "offsetRects" in json
            else None,
            [Rectangle(s) for s in json["scrollRects"]]
            if "scrollRects" in json
            else None,
            [Rectangle(c) for c in json["clientRects"]]
            if "clientRects" in json
            else None,
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "nodeIndex": self.nodeIndex,
                "styles": [s.to_json() for s in self.styles],
                "bounds": [list(b) for b in self.bounds],
                "text": [int(t) for t in self.text],
                "stackingContexts": self.stackingContexts.to_json(),
                "paintOrders": self.paintOrders,
                "offsetRects": [list(o) for o in self.offsetRects]
                if self.offsetRects
                else None,
                "scrollRects": [list(s) for s in self.scrollRects]
                if self.scrollRects
                else None,
                "clientRects": [list(c) for c in self.clientRects]
                if self.clientRects
                else None,
            }
        )


@dataclasses.dataclass
class TextBoxSnapshot:
    """Table of details of the post layout rendered text positions. The exact layout should not be regarded as
    stable and may change between versions.

    Attributes
    ----------
    layoutIndex: list[int]
            Index of the layout tree node that owns this box collection.
    bounds: list[Rectangle]
            The absolute position bounding box.
    start: list[int]
            The starting index in characters, for this post layout textbox substring. Characters that
            would be represented as a surrogate pair in UTF-16 have length 2.
    length: list[int]
            The number of characters in this post layout textbox substring. Characters that would be
            represented as a surrogate pair in UTF-16 have length 2.
    """

    layoutIndex: list[int]
    bounds: list[Rectangle]
    start: list[int]
    length: list[int]

    @classmethod
    def from_json(cls, json: dict) -> TextBoxSnapshot:
        return cls(
            json["layoutIndex"],
            [Rectangle(b) for b in json["bounds"]],
            json["start"],
            json["length"],
        )

    def to_json(self) -> dict:
        return {
            "layoutIndex": self.layoutIndex,
            "bounds": [list(b) for b in self.bounds],
            "start": self.start,
            "length": self.length,
        }


def disable():
    """Disables DOM snapshot agent for the given page."""
    return {"method": "DOMSnapshot.disable", "params": {}}


def enable():
    """Enables DOM snapshot agent for the given page."""
    return {"method": "DOMSnapshot.enable", "params": {}}


def get_snapshot(
    computedStyleWhitelist: list[str],
    includeEventListeners: Optional[bool] = None,
    includePaintOrder: Optional[bool] = None,
    includeUserAgentShadowTree: Optional[bool] = None,
):
    """Returns a document snapshot, including the full DOM tree of the root node (including iframes,
    template contents, and imported documents) in a flattened array, as well as layout and
    white-listed computed style information for the nodes. Shadow DOM in the returned DOM tree is
    flattened.

    **Deprectated**

    Parameters
    ----------
    computedStyleWhitelist: list[str]
            Whitelist of computed styles to return.
    includeEventListeners: Optional[bool]
            Whether or not to retrieve details of DOM listeners (default false).
    includePaintOrder: Optional[bool]
            Whether to determine and include the paint order index of LayoutTreeNodes (default false).
    includeUserAgentShadowTree: Optional[bool]
            Whether to include UA shadow tree in the snapshot (default false).

    Returns
    -------
    domNodes: list[DOMNode]
            The nodes in the DOM tree. The DOMNode at index 0 corresponds to the root document.
    layoutTreeNodes: list[LayoutTreeNode]
            The nodes in the layout tree.
    computedStyles: list[ComputedStyle]
            Whitelisted ComputedStyle properties for each node in the layout tree.
    """
    return filter_unset_parameters(
        {
            "method": "DOMSnapshot.getSnapshot",
            "params": {
                "computedStyleWhitelist": computedStyleWhitelist,
                "includeEventListeners": includeEventListeners,
                "includePaintOrder": includePaintOrder,
                "includeUserAgentShadowTree": includeUserAgentShadowTree,
            },
        }
    )


def parse_get_snapshot_response(response):
    return {
        "domNodes": [DOMNode.from_json(d) for d in response["domNodes"]],
        "layoutTreeNodes": [
            LayoutTreeNode.from_json(l) for l in response["layoutTreeNodes"]
        ],
        "computedStyles": [
            ComputedStyle.from_json(c) for c in response["computedStyles"]
        ],
    }


def capture_snapshot(
    computedStyles: list[str],
    includePaintOrder: Optional[bool] = None,
    includeDOMRects: Optional[bool] = None,
):
    """Returns a document snapshot, including the full DOM tree of the root node (including iframes,
    template contents, and imported documents) in a flattened array, as well as layout and
    white-listed computed style information for the nodes. Shadow DOM in the returned DOM tree is
    flattened.

    Parameters
    ----------
    computedStyles: list[str]
            Whitelist of computed styles to return.
    includePaintOrder: Optional[bool]
            Whether to include layout object paint orders into the snapshot.
    includeDOMRects: Optional[bool]
            Whether to include DOM rectangles (offsetRects, clientRects, scrollRects) into the snapshot

    Returns
    -------
    documents: list[DocumentSnapshot]
            The nodes in the DOM tree. The DOMNode at index 0 corresponds to the root document.
    strings: list[str]
            Shared string table that all string properties refer to with indexes.
    """
    return filter_unset_parameters(
        {
            "method": "DOMSnapshot.captureSnapshot",
            "params": {
                "computedStyles": computedStyles,
                "includePaintOrder": includePaintOrder,
                "includeDOMRects": includeDOMRects,
            },
        }
    )


def parse_capture_snapshot_response(response):
    return {
        "documents": [DocumentSnapshot.from_json(d) for d in response["documents"]],
        "strings": response["strings"],
    }
