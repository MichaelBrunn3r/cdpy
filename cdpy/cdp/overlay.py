from __future__ import annotations

import dataclasses
import enum
from typing import Generator, Optional

from . import dom, page, runtime
from ._utils import filter_none


@dataclasses.dataclass
class SourceOrderConfig:
    """Configuration data for drawing the source order of an elements children.

    Attributes
    ----------
    parentOutlineColor: dom.RGBA
            the color to outline the givent element in.
    childOutlineColor: dom.RGBA
            the color to outline the child elements in.
    """

    parentOutlineColor: dom.RGBA
    childOutlineColor: dom.RGBA

    @classmethod
    def from_json(cls, json: dict) -> SourceOrderConfig:
        return cls(
            dom.RGBA.from_json(json["parentOutlineColor"]),
            dom.RGBA.from_json(json["childOutlineColor"]),
        )

    def to_json(self) -> dict:
        return {
            "parentOutlineColor": self.parentOutlineColor.to_json(),
            "childOutlineColor": self.childOutlineColor.to_json(),
        }


@dataclasses.dataclass
class GridHighlightConfig:
    """Configuration data for the highlighting of Grid elements.

    Attributes
    ----------
    showGridExtensionLines: Optional[bool]
            Whether the extension lines from grid cells to the rulers should be shown (default: false).
    showPositiveLineNumbers: Optional[bool]
            Show Positive line number labels (default: false).
    showNegativeLineNumbers: Optional[bool]
            Show Negative line number labels (default: false).
    showAreaNames: Optional[bool]
            Show area name labels (default: false).
    showLineNames: Optional[bool]
            Show line name labels (default: false).
    showTrackSizes: Optional[bool]
            Show track size labels (default: false).
    gridBorderColor: Optional[dom.RGBA]
            The grid container border highlight color (default: transparent).
    cellBorderColor: Optional[dom.RGBA]
            The cell border color (default: transparent). Deprecated, please use rowLineColor and columnLineColor instead.
    rowLineColor: Optional[dom.RGBA]
            The row line color (default: transparent).
    columnLineColor: Optional[dom.RGBA]
            The column line color (default: transparent).
    gridBorderDash: Optional[bool]
            Whether the grid border is dashed (default: false).
    cellBorderDash: Optional[bool]
            Whether the cell border is dashed (default: false). Deprecated, please us rowLineDash and columnLineDash instead.
    rowLineDash: Optional[bool]
            Whether row lines are dashed (default: false).
    columnLineDash: Optional[bool]
            Whether column lines are dashed (default: false).
    rowGapColor: Optional[dom.RGBA]
            The row gap highlight fill color (default: transparent).
    rowHatchColor: Optional[dom.RGBA]
            The row gap hatching fill color (default: transparent).
    columnGapColor: Optional[dom.RGBA]
            The column gap highlight fill color (default: transparent).
    columnHatchColor: Optional[dom.RGBA]
            The column gap hatching fill color (default: transparent).
    areaBorderColor: Optional[dom.RGBA]
            The named grid areas border color (Default: transparent).
    gridBackgroundColor: Optional[dom.RGBA]
            The grid container background color (Default: transparent).
    """

    showGridExtensionLines: Optional[bool] = None
    showPositiveLineNumbers: Optional[bool] = None
    showNegativeLineNumbers: Optional[bool] = None
    showAreaNames: Optional[bool] = None
    showLineNames: Optional[bool] = None
    showTrackSizes: Optional[bool] = None
    gridBorderColor: Optional[dom.RGBA] = None
    cellBorderColor: Optional[dom.RGBA] = None
    rowLineColor: Optional[dom.RGBA] = None
    columnLineColor: Optional[dom.RGBA] = None
    gridBorderDash: Optional[bool] = None
    cellBorderDash: Optional[bool] = None
    rowLineDash: Optional[bool] = None
    columnLineDash: Optional[bool] = None
    rowGapColor: Optional[dom.RGBA] = None
    rowHatchColor: Optional[dom.RGBA] = None
    columnGapColor: Optional[dom.RGBA] = None
    columnHatchColor: Optional[dom.RGBA] = None
    areaBorderColor: Optional[dom.RGBA] = None
    gridBackgroundColor: Optional[dom.RGBA] = None

    @classmethod
    def from_json(cls, json: dict) -> GridHighlightConfig:
        return cls(
            json.get("showGridExtensionLines"),
            json.get("showPositiveLineNumbers"),
            json.get("showNegativeLineNumbers"),
            json.get("showAreaNames"),
            json.get("showLineNames"),
            json.get("showTrackSizes"),
            dom.RGBA.from_json(json["gridBorderColor"])
            if "gridBorderColor" in json
            else None,
            dom.RGBA.from_json(json["cellBorderColor"])
            if "cellBorderColor" in json
            else None,
            dom.RGBA.from_json(json["rowLineColor"])
            if "rowLineColor" in json
            else None,
            dom.RGBA.from_json(json["columnLineColor"])
            if "columnLineColor" in json
            else None,
            json.get("gridBorderDash"),
            json.get("cellBorderDash"),
            json.get("rowLineDash"),
            json.get("columnLineDash"),
            dom.RGBA.from_json(json["rowGapColor"]) if "rowGapColor" in json else None,
            dom.RGBA.from_json(json["rowHatchColor"])
            if "rowHatchColor" in json
            else None,
            dom.RGBA.from_json(json["columnGapColor"])
            if "columnGapColor" in json
            else None,
            dom.RGBA.from_json(json["columnHatchColor"])
            if "columnHatchColor" in json
            else None,
            dom.RGBA.from_json(json["areaBorderColor"])
            if "areaBorderColor" in json
            else None,
            dom.RGBA.from_json(json["gridBackgroundColor"])
            if "gridBackgroundColor" in json
            else None,
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "showGridExtensionLines": self.showGridExtensionLines,
                "showPositiveLineNumbers": self.showPositiveLineNumbers,
                "showNegativeLineNumbers": self.showNegativeLineNumbers,
                "showAreaNames": self.showAreaNames,
                "showLineNames": self.showLineNames,
                "showTrackSizes": self.showTrackSizes,
                "gridBorderColor": self.gridBorderColor.to_json()
                if self.gridBorderColor
                else None,
                "cellBorderColor": self.cellBorderColor.to_json()
                if self.cellBorderColor
                else None,
                "rowLineColor": self.rowLineColor.to_json()
                if self.rowLineColor
                else None,
                "columnLineColor": self.columnLineColor.to_json()
                if self.columnLineColor
                else None,
                "gridBorderDash": self.gridBorderDash,
                "cellBorderDash": self.cellBorderDash,
                "rowLineDash": self.rowLineDash,
                "columnLineDash": self.columnLineDash,
                "rowGapColor": self.rowGapColor.to_json() if self.rowGapColor else None,
                "rowHatchColor": self.rowHatchColor.to_json()
                if self.rowHatchColor
                else None,
                "columnGapColor": self.columnGapColor.to_json()
                if self.columnGapColor
                else None,
                "columnHatchColor": self.columnHatchColor.to_json()
                if self.columnHatchColor
                else None,
                "areaBorderColor": self.areaBorderColor.to_json()
                if self.areaBorderColor
                else None,
                "gridBackgroundColor": self.gridBackgroundColor.to_json()
                if self.gridBackgroundColor
                else None,
            }
        )


@dataclasses.dataclass
class FlexContainerHighlightConfig:
    """Configuration data for the highlighting of Flex container elements.

    Attributes
    ----------
    containerBorder: Optional[LineStyle]
            The style of the container border
    lineSeparator: Optional[LineStyle]
            The style of the separator between lines
    itemSeparator: Optional[LineStyle]
            The style of the separator between items
    mainDistributedSpace: Optional[BoxStyle]
            Style of content-distribution space on the main axis (justify-content).
    crossDistributedSpace: Optional[BoxStyle]
            Style of content-distribution space on the cross axis (align-content).
    rowGapSpace: Optional[BoxStyle]
            Style of empty space caused by row gaps (gap/row-gap).
    columnGapSpace: Optional[BoxStyle]
            Style of empty space caused by columns gaps (gap/column-gap).
    crossAlignment: Optional[LineStyle]
            Style of the self-alignment line (align-items).
    """

    containerBorder: Optional[LineStyle] = None
    lineSeparator: Optional[LineStyle] = None
    itemSeparator: Optional[LineStyle] = None
    mainDistributedSpace: Optional[BoxStyle] = None
    crossDistributedSpace: Optional[BoxStyle] = None
    rowGapSpace: Optional[BoxStyle] = None
    columnGapSpace: Optional[BoxStyle] = None
    crossAlignment: Optional[LineStyle] = None

    @classmethod
    def from_json(cls, json: dict) -> FlexContainerHighlightConfig:
        return cls(
            LineStyle.from_json(json["containerBorder"])
            if "containerBorder" in json
            else None,
            LineStyle.from_json(json["lineSeparator"])
            if "lineSeparator" in json
            else None,
            LineStyle.from_json(json["itemSeparator"])
            if "itemSeparator" in json
            else None,
            BoxStyle.from_json(json["mainDistributedSpace"])
            if "mainDistributedSpace" in json
            else None,
            BoxStyle.from_json(json["crossDistributedSpace"])
            if "crossDistributedSpace" in json
            else None,
            BoxStyle.from_json(json["rowGapSpace"]) if "rowGapSpace" in json else None,
            BoxStyle.from_json(json["columnGapSpace"])
            if "columnGapSpace" in json
            else None,
            LineStyle.from_json(json["crossAlignment"])
            if "crossAlignment" in json
            else None,
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "containerBorder": self.containerBorder.to_json()
                if self.containerBorder
                else None,
                "lineSeparator": self.lineSeparator.to_json()
                if self.lineSeparator
                else None,
                "itemSeparator": self.itemSeparator.to_json()
                if self.itemSeparator
                else None,
                "mainDistributedSpace": self.mainDistributedSpace.to_json()
                if self.mainDistributedSpace
                else None,
                "crossDistributedSpace": self.crossDistributedSpace.to_json()
                if self.crossDistributedSpace
                else None,
                "rowGapSpace": self.rowGapSpace.to_json() if self.rowGapSpace else None,
                "columnGapSpace": self.columnGapSpace.to_json()
                if self.columnGapSpace
                else None,
                "crossAlignment": self.crossAlignment.to_json()
                if self.crossAlignment
                else None,
            }
        )


@dataclasses.dataclass
class FlexItemHighlightConfig:
    """Configuration data for the highlighting of Flex item elements.

    Attributes
    ----------
    baseSizeBox: Optional[BoxStyle]
            Style of the box representing the item's base size
    baseSizeBorder: Optional[LineStyle]
            Style of the border around the box representing the item's base size
    flexibilityArrow: Optional[LineStyle]
            Style of the arrow representing if the item grew or shrank
    """

    baseSizeBox: Optional[BoxStyle] = None
    baseSizeBorder: Optional[LineStyle] = None
    flexibilityArrow: Optional[LineStyle] = None

    @classmethod
    def from_json(cls, json: dict) -> FlexItemHighlightConfig:
        return cls(
            BoxStyle.from_json(json["baseSizeBox"]) if "baseSizeBox" in json else None,
            LineStyle.from_json(json["baseSizeBorder"])
            if "baseSizeBorder" in json
            else None,
            LineStyle.from_json(json["flexibilityArrow"])
            if "flexibilityArrow" in json
            else None,
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "baseSizeBox": self.baseSizeBox.to_json() if self.baseSizeBox else None,
                "baseSizeBorder": self.baseSizeBorder.to_json()
                if self.baseSizeBorder
                else None,
                "flexibilityArrow": self.flexibilityArrow.to_json()
                if self.flexibilityArrow
                else None,
            }
        )


@dataclasses.dataclass
class LineStyle:
    """Style information for drawing a line.

    Attributes
    ----------
    color: Optional[dom.RGBA]
            The color of the line (default: transparent)
    pattern: Optional[str]
            The line pattern (default: solid)
    """

    color: Optional[dom.RGBA] = None
    pattern: Optional[str] = None

    @classmethod
    def from_json(cls, json: dict) -> LineStyle:
        return cls(
            dom.RGBA.from_json(json["color"]) if "color" in json else None,
            json.get("pattern"),
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "color": self.color.to_json() if self.color else None,
                "pattern": self.pattern,
            }
        )


@dataclasses.dataclass
class BoxStyle:
    """Style information for drawing a box.

    Attributes
    ----------
    fillColor: Optional[dom.RGBA]
            The background color for the box (default: transparent)
    hatchColor: Optional[dom.RGBA]
            The hatching color for the box (default: transparent)
    """

    fillColor: Optional[dom.RGBA] = None
    hatchColor: Optional[dom.RGBA] = None

    @classmethod
    def from_json(cls, json: dict) -> BoxStyle:
        return cls(
            dom.RGBA.from_json(json["fillColor"]) if "fillColor" in json else None,
            dom.RGBA.from_json(json["hatchColor"]) if "hatchColor" in json else None,
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "fillColor": self.fillColor.to_json() if self.fillColor else None,
                "hatchColor": self.hatchColor.to_json() if self.hatchColor else None,
            }
        )


class ContrastAlgorithm(enum.Enum):
    """"""

    AA = "aa"
    AAA = "aaa"
    APCA = "apca"


@dataclasses.dataclass
class HighlightConfig:
    """Configuration data for the highlighting of page elements.

    Attributes
    ----------
    showInfo: Optional[bool]
            Whether the node info tooltip should be shown (default: false).
    showStyles: Optional[bool]
            Whether the node styles in the tooltip (default: false).
    showRulers: Optional[bool]
            Whether the rulers should be shown (default: false).
    showAccessibilityInfo: Optional[bool]
            Whether the a11y info should be shown (default: true).
    showExtensionLines: Optional[bool]
            Whether the extension lines from node to the rulers should be shown (default: false).
    contentColor: Optional[dom.RGBA]
            The content box highlight fill color (default: transparent).
    paddingColor: Optional[dom.RGBA]
            The padding highlight fill color (default: transparent).
    borderColor: Optional[dom.RGBA]
            The border highlight fill color (default: transparent).
    marginColor: Optional[dom.RGBA]
            The margin highlight fill color (default: transparent).
    eventTargetColor: Optional[dom.RGBA]
            The event target element highlight fill color (default: transparent).
    shapeColor: Optional[dom.RGBA]
            The shape outside fill color (default: transparent).
    shapeMarginColor: Optional[dom.RGBA]
            The shape margin fill color (default: transparent).
    cssGridColor: Optional[dom.RGBA]
            The grid layout color (default: transparent).
    colorFormat: Optional[ColorFormat]
            The color format used to format color styles (default: hex).
    gridHighlightConfig: Optional[GridHighlightConfig]
            The grid layout highlight configuration (default: all transparent).
    flexContainerHighlightConfig: Optional[FlexContainerHighlightConfig]
            The flex container highlight configuration (default: all transparent).
    flexItemHighlightConfig: Optional[FlexItemHighlightConfig]
            The flex item highlight configuration (default: all transparent).
    contrastAlgorithm: Optional[ContrastAlgorithm]
            The contrast algorithm to use for the contrast ratio (default: aa).
    """

    showInfo: Optional[bool] = None
    showStyles: Optional[bool] = None
    showRulers: Optional[bool] = None
    showAccessibilityInfo: Optional[bool] = None
    showExtensionLines: Optional[bool] = None
    contentColor: Optional[dom.RGBA] = None
    paddingColor: Optional[dom.RGBA] = None
    borderColor: Optional[dom.RGBA] = None
    marginColor: Optional[dom.RGBA] = None
    eventTargetColor: Optional[dom.RGBA] = None
    shapeColor: Optional[dom.RGBA] = None
    shapeMarginColor: Optional[dom.RGBA] = None
    cssGridColor: Optional[dom.RGBA] = None
    colorFormat: Optional[ColorFormat] = None
    gridHighlightConfig: Optional[GridHighlightConfig] = None
    flexContainerHighlightConfig: Optional[FlexContainerHighlightConfig] = None
    flexItemHighlightConfig: Optional[FlexItemHighlightConfig] = None
    contrastAlgorithm: Optional[ContrastAlgorithm] = None

    @classmethod
    def from_json(cls, json: dict) -> HighlightConfig:
        return cls(
            json.get("showInfo"),
            json.get("showStyles"),
            json.get("showRulers"),
            json.get("showAccessibilityInfo"),
            json.get("showExtensionLines"),
            dom.RGBA.from_json(json["contentColor"])
            if "contentColor" in json
            else None,
            dom.RGBA.from_json(json["paddingColor"])
            if "paddingColor" in json
            else None,
            dom.RGBA.from_json(json["borderColor"]) if "borderColor" in json else None,
            dom.RGBA.from_json(json["marginColor"]) if "marginColor" in json else None,
            dom.RGBA.from_json(json["eventTargetColor"])
            if "eventTargetColor" in json
            else None,
            dom.RGBA.from_json(json["shapeColor"]) if "shapeColor" in json else None,
            dom.RGBA.from_json(json["shapeMarginColor"])
            if "shapeMarginColor" in json
            else None,
            dom.RGBA.from_json(json["cssGridColor"])
            if "cssGridColor" in json
            else None,
            ColorFormat(json["colorFormat"]) if "colorFormat" in json else None,
            GridHighlightConfig.from_json(json["gridHighlightConfig"])
            if "gridHighlightConfig" in json
            else None,
            FlexContainerHighlightConfig.from_json(json["flexContainerHighlightConfig"])
            if "flexContainerHighlightConfig" in json
            else None,
            FlexItemHighlightConfig.from_json(json["flexItemHighlightConfig"])
            if "flexItemHighlightConfig" in json
            else None,
            ContrastAlgorithm(json["contrastAlgorithm"])
            if "contrastAlgorithm" in json
            else None,
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "showInfo": self.showInfo,
                "showStyles": self.showStyles,
                "showRulers": self.showRulers,
                "showAccessibilityInfo": self.showAccessibilityInfo,
                "showExtensionLines": self.showExtensionLines,
                "contentColor": self.contentColor.to_json()
                if self.contentColor
                else None,
                "paddingColor": self.paddingColor.to_json()
                if self.paddingColor
                else None,
                "borderColor": self.borderColor.to_json() if self.borderColor else None,
                "marginColor": self.marginColor.to_json() if self.marginColor else None,
                "eventTargetColor": self.eventTargetColor.to_json()
                if self.eventTargetColor
                else None,
                "shapeColor": self.shapeColor.to_json() if self.shapeColor else None,
                "shapeMarginColor": self.shapeMarginColor.to_json()
                if self.shapeMarginColor
                else None,
                "cssGridColor": self.cssGridColor.to_json()
                if self.cssGridColor
                else None,
                "colorFormat": self.colorFormat.value if self.colorFormat else None,
                "gridHighlightConfig": self.gridHighlightConfig.to_json()
                if self.gridHighlightConfig
                else None,
                "flexContainerHighlightConfig": self.flexContainerHighlightConfig.to_json()
                if self.flexContainerHighlightConfig
                else None,
                "flexItemHighlightConfig": self.flexItemHighlightConfig.to_json()
                if self.flexItemHighlightConfig
                else None,
                "contrastAlgorithm": self.contrastAlgorithm.value
                if self.contrastAlgorithm
                else None,
            }
        )


class ColorFormat(enum.Enum):
    """"""

    RGB = "rgb"
    HSL = "hsl"
    HEX = "hex"


@dataclasses.dataclass
class GridNodeHighlightConfig:
    """Configurations for Persistent Grid Highlight

    Attributes
    ----------
    gridHighlightConfig: GridHighlightConfig
            A descriptor for the highlight appearance.
    nodeId: dom.NodeId
            Identifier of the node to highlight.
    """

    gridHighlightConfig: GridHighlightConfig
    nodeId: dom.NodeId

    @classmethod
    def from_json(cls, json: dict) -> GridNodeHighlightConfig:
        return cls(
            GridHighlightConfig.from_json(json["gridHighlightConfig"]),
            dom.NodeId(json["nodeId"]),
        )

    def to_json(self) -> dict:
        return {
            "gridHighlightConfig": self.gridHighlightConfig.to_json(),
            "nodeId": int(self.nodeId),
        }


@dataclasses.dataclass
class FlexNodeHighlightConfig:
    """
    Attributes
    ----------
    flexContainerHighlightConfig: FlexContainerHighlightConfig
            A descriptor for the highlight appearance of flex containers.
    nodeId: dom.NodeId
            Identifier of the node to highlight.
    """

    flexContainerHighlightConfig: FlexContainerHighlightConfig
    nodeId: dom.NodeId

    @classmethod
    def from_json(cls, json: dict) -> FlexNodeHighlightConfig:
        return cls(
            FlexContainerHighlightConfig.from_json(
                json["flexContainerHighlightConfig"]
            ),
            dom.NodeId(json["nodeId"]),
        )

    def to_json(self) -> dict:
        return {
            "flexContainerHighlightConfig": self.flexContainerHighlightConfig.to_json(),
            "nodeId": int(self.nodeId),
        }


@dataclasses.dataclass
class HingeConfig:
    """Configuration for dual screen hinge

    Attributes
    ----------
    rect: dom.Rect
            A rectangle represent hinge
    contentColor: Optional[dom.RGBA]
            The content box highlight fill color (default: a dark color).
    outlineColor: Optional[dom.RGBA]
            The content box highlight outline color (default: transparent).
    """

    rect: dom.Rect
    contentColor: Optional[dom.RGBA] = None
    outlineColor: Optional[dom.RGBA] = None

    @classmethod
    def from_json(cls, json: dict) -> HingeConfig:
        return cls(
            dom.Rect.from_json(json["rect"]),
            dom.RGBA.from_json(json["contentColor"])
            if "contentColor" in json
            else None,
            dom.RGBA.from_json(json["outlineColor"])
            if "outlineColor" in json
            else None,
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "rect": self.rect.to_json(),
                "contentColor": self.contentColor.to_json()
                if self.contentColor
                else None,
                "outlineColor": self.outlineColor.to_json()
                if self.outlineColor
                else None,
            }
        )


class InspectMode(enum.Enum):
    """"""

    SEARCH_FOR_NODE = "searchForNode"
    SEARCH_FOR_UA_SHADOW_DOM = "searchForUAShadowDOM"
    CAPTURE_AREA_SCREENSHOT = "captureAreaScreenshot"
    SHOW_DISTANCES = "showDistances"
    NONE = "none"


def disable() -> dict:
    """Disables domain notifications."""
    return {"method": "Overlay.disable", "params": {}}


def enable() -> dict:
    """Enables domain notifications."""
    return {"method": "Overlay.enable", "params": {}}


def get_highlight_object_for_test(
    nodeId: dom.NodeId,
    includeDistance: Optional[bool] = None,
    includeStyle: Optional[bool] = None,
    colorFormat: Optional[ColorFormat] = None,
    showAccessibilityInfo: Optional[bool] = None,
) -> Generator[dict, dict, dict]:
    """For testing.

    Parameters
    ----------
    nodeId: dom.NodeId
            Id of the node to get highlight object for.
    includeDistance: Optional[bool]
            Whether to include distance info.
    includeStyle: Optional[bool]
            Whether to include style info.
    colorFormat: Optional[ColorFormat]
            The color format to get config with (default: hex).
    showAccessibilityInfo: Optional[bool]
            Whether to show accessibility info (default: true).

    Returns
    -------
    highlight: dict
            Highlight data for the node.
    """
    response = yield {
        "method": "Overlay.getHighlightObjectForTest",
        "params": filter_none(
            {
                "nodeId": int(nodeId),
                "includeDistance": includeDistance,
                "includeStyle": includeStyle,
                "colorFormat": colorFormat.value if colorFormat else None,
                "showAccessibilityInfo": showAccessibilityInfo,
            }
        ),
    }
    return response["highlight"]


def get_grid_highlight_objects_for_test(
    nodeIds: list[dom.NodeId],
) -> Generator[dict, dict, dict]:
    """For Persistent Grid testing.

    Parameters
    ----------
    nodeIds: list[dom.NodeId]
            Ids of the node to get highlight object for.

    Returns
    -------
    highlights: dict
            Grid Highlight data for the node ids provided.
    """
    response = yield {
        "method": "Overlay.getGridHighlightObjectsForTest",
        "params": {"nodeIds": [int(n) for n in nodeIds]},
    }
    return response["highlights"]


def get_source_order_highlight_object_for_test(
    nodeId: dom.NodeId,
) -> Generator[dict, dict, dict]:
    """For Source Order Viewer testing.

    Parameters
    ----------
    nodeId: dom.NodeId
            Id of the node to highlight.

    Returns
    -------
    highlight: dict
            Source order highlight data for the node id provided.
    """
    response = yield {
        "method": "Overlay.getSourceOrderHighlightObjectForTest",
        "params": {"nodeId": int(nodeId)},
    }
    return response["highlight"]


def hide_highlight() -> dict:
    """Hides any highlight."""
    return {"method": "Overlay.hideHighlight", "params": {}}


def highlight_frame(
    frameId: page.FrameId,
    contentColor: Optional[dom.RGBA] = None,
    contentOutlineColor: Optional[dom.RGBA] = None,
) -> dict:
    """Highlights owner element of the frame with given id.

    Parameters
    ----------
    frameId: page.FrameId
            Identifier of the frame to highlight.
    contentColor: Optional[dom.RGBA]
            The content box highlight fill color (default: transparent).
    contentOutlineColor: Optional[dom.RGBA]
            The content box highlight outline color (default: transparent).
    """
    return {
        "method": "Overlay.highlightFrame",
        "params": filter_none(
            {
                "frameId": str(frameId),
                "contentColor": contentColor.to_json() if contentColor else None,
                "contentOutlineColor": contentOutlineColor.to_json()
                if contentOutlineColor
                else None,
            }
        ),
    }


def highlight_node(
    highlightConfig: HighlightConfig,
    nodeId: Optional[dom.NodeId] = None,
    backendNodeId: Optional[dom.BackendNodeId] = None,
    objectId: Optional[runtime.RemoteObjectId] = None,
    selector: Optional[str] = None,
) -> dict:
    """Highlights DOM node with given id or with the given JavaScript object wrapper. Either nodeId or
    objectId must be specified.

    Parameters
    ----------
    highlightConfig: HighlightConfig
            A descriptor for the highlight appearance.
    nodeId: Optional[dom.NodeId]
            Identifier of the node to highlight.
    backendNodeId: Optional[dom.BackendNodeId]
            Identifier of the backend node to highlight.
    objectId: Optional[runtime.RemoteObjectId]
            JavaScript object id of the node to be highlighted.
    selector: Optional[str]
            Selectors to highlight relevant nodes.
    """
    return {
        "method": "Overlay.highlightNode",
        "params": filter_none(
            {
                "highlightConfig": highlightConfig.to_json(),
                "nodeId": int(nodeId) if nodeId else None,
                "backendNodeId": int(backendNodeId) if backendNodeId else None,
                "objectId": str(objectId) if objectId else None,
                "selector": selector,
            }
        ),
    }


def highlight_quad(
    quad: dom.Quad,
    color: Optional[dom.RGBA] = None,
    outlineColor: Optional[dom.RGBA] = None,
) -> dict:
    """Highlights given quad. Coordinates are absolute with respect to the main frame viewport.

    Parameters
    ----------
    quad: dom.Quad
            Quad to highlight
    color: Optional[dom.RGBA]
            The highlight fill color (default: transparent).
    outlineColor: Optional[dom.RGBA]
            The highlight outline color (default: transparent).
    """
    return {
        "method": "Overlay.highlightQuad",
        "params": filter_none(
            {
                "quad": list(quad),
                "color": color.to_json() if color else None,
                "outlineColor": outlineColor.to_json() if outlineColor else None,
            }
        ),
    }


def highlight_rect(
    x: int,
    y: int,
    width: int,
    height: int,
    color: Optional[dom.RGBA] = None,
    outlineColor: Optional[dom.RGBA] = None,
) -> dict:
    """Highlights given rectangle. Coordinates are absolute with respect to the main frame viewport.

    Parameters
    ----------
    x: int
            X coordinate
    y: int
            Y coordinate
    width: int
            Rectangle width
    height: int
            Rectangle height
    color: Optional[dom.RGBA]
            The highlight fill color (default: transparent).
    outlineColor: Optional[dom.RGBA]
            The highlight outline color (default: transparent).
    """
    return {
        "method": "Overlay.highlightRect",
        "params": filter_none(
            {
                "x": x,
                "y": y,
                "width": width,
                "height": height,
                "color": color.to_json() if color else None,
                "outlineColor": outlineColor.to_json() if outlineColor else None,
            }
        ),
    }


def highlight_source_order(
    sourceOrderConfig: SourceOrderConfig,
    nodeId: Optional[dom.NodeId] = None,
    backendNodeId: Optional[dom.BackendNodeId] = None,
    objectId: Optional[runtime.RemoteObjectId] = None,
) -> dict:
    """Highlights the source order of the children of the DOM node with given id or with the given
    JavaScript object wrapper. Either nodeId or objectId must be specified.

    Parameters
    ----------
    sourceOrderConfig: SourceOrderConfig
            A descriptor for the appearance of the overlay drawing.
    nodeId: Optional[dom.NodeId]
            Identifier of the node to highlight.
    backendNodeId: Optional[dom.BackendNodeId]
            Identifier of the backend node to highlight.
    objectId: Optional[runtime.RemoteObjectId]
            JavaScript object id of the node to be highlighted.
    """
    return {
        "method": "Overlay.highlightSourceOrder",
        "params": filter_none(
            {
                "sourceOrderConfig": sourceOrderConfig.to_json(),
                "nodeId": int(nodeId) if nodeId else None,
                "backendNodeId": int(backendNodeId) if backendNodeId else None,
                "objectId": str(objectId) if objectId else None,
            }
        ),
    }


def set_inspect_mode(
    mode: InspectMode, highlightConfig: Optional[HighlightConfig] = None
) -> dict:
    """Enters the 'inspect' mode. In this mode, elements that user is hovering over are highlighted.
    Backend then generates 'inspectNodeRequested' event upon element selection.

    Parameters
    ----------
    mode: InspectMode
            Set an inspection mode.
    highlightConfig: Optional[HighlightConfig]
            A descriptor for the highlight appearance of hovered-over nodes. May be omitted if `enabled
            == false`.
    """
    return {
        "method": "Overlay.setInspectMode",
        "params": filter_none(
            {
                "mode": mode.value,
                "highlightConfig": highlightConfig.to_json()
                if highlightConfig
                else None,
            }
        ),
    }


def set_show_ad_highlights(show: bool) -> dict:
    """Highlights owner element of all frames detected to be ads.

    Parameters
    ----------
    show: bool
            True for showing ad highlights
    """
    return {"method": "Overlay.setShowAdHighlights", "params": {"show": show}}


def set_paused_in_debugger_message(message: Optional[str] = None) -> dict:
    """
    Parameters
    ----------
    message: Optional[str]
            The message to display, also triggers resume and step over controls.
    """
    return {
        "method": "Overlay.setPausedInDebuggerMessage",
        "params": filter_none({"message": message}),
    }


def set_show_debug_borders(show: bool) -> dict:
    """Requests that backend shows debug borders on layers

    Parameters
    ----------
    show: bool
            True for showing debug borders
    """
    return {"method": "Overlay.setShowDebugBorders", "params": {"show": show}}


def set_show_fps_counter(show: bool) -> dict:
    """Requests that backend shows the FPS counter

    Parameters
    ----------
    show: bool
            True for showing the FPS counter
    """
    return {"method": "Overlay.setShowFPSCounter", "params": {"show": show}}


def set_show_grid_overlays(
    gridNodeHighlightConfigs: list[GridNodeHighlightConfig],
) -> dict:
    """Highlight multiple elements with the CSS Grid overlay.

    Parameters
    ----------
    gridNodeHighlightConfigs: list[GridNodeHighlightConfig]
            An array of node identifiers and descriptors for the highlight appearance.
    """
    return {
        "method": "Overlay.setShowGridOverlays",
        "params": {
            "gridNodeHighlightConfigs": [g.to_json() for g in gridNodeHighlightConfigs]
        },
    }


def set_show_flex_overlays(
    flexNodeHighlightConfigs: list[FlexNodeHighlightConfig],
) -> dict:
    """
    Parameters
    ----------
    flexNodeHighlightConfigs: list[FlexNodeHighlightConfig]
            An array of node identifiers and descriptors for the highlight appearance.
    """
    return {
        "method": "Overlay.setShowFlexOverlays",
        "params": {
            "flexNodeHighlightConfigs": [f.to_json() for f in flexNodeHighlightConfigs]
        },
    }


def set_show_paint_rects(result: bool) -> dict:
    """Requests that backend shows paint rectangles

    Parameters
    ----------
    result: bool
            True for showing paint rectangles
    """
    return {"method": "Overlay.setShowPaintRects", "params": {"result": result}}


def set_show_layout_shift_regions(result: bool) -> dict:
    """Requests that backend shows layout shift regions

    Parameters
    ----------
    result: bool
            True for showing layout shift regions
    """
    return {"method": "Overlay.setShowLayoutShiftRegions", "params": {"result": result}}


def set_show_scroll_bottleneck_rects(show: bool) -> dict:
    """Requests that backend shows scroll bottleneck rects

    Parameters
    ----------
    show: bool
            True for showing scroll bottleneck rects
    """
    return {"method": "Overlay.setShowScrollBottleneckRects", "params": {"show": show}}


def set_show_hit_test_borders(show: bool) -> dict:
    """Requests that backend shows hit-test borders on layers

    Parameters
    ----------
    show: bool
            True for showing hit-test borders
    """
    return {"method": "Overlay.setShowHitTestBorders", "params": {"show": show}}


def set_show_web_vitals(show: bool) -> dict:
    """Request that backend shows an overlay with web vital metrics.

    Parameters
    ----------
    show: bool
    """
    return {"method": "Overlay.setShowWebVitals", "params": {"show": show}}


def set_show_viewport_size_on_resize(show: bool) -> dict:
    """Paints viewport size upon main frame resize.

    Parameters
    ----------
    show: bool
            Whether to paint size or not.
    """
    return {"method": "Overlay.setShowViewportSizeOnResize", "params": {"show": show}}


def set_show_hinge(hingeConfig: Optional[HingeConfig] = None) -> dict:
    """Add a dual screen device hinge

    Parameters
    ----------
    hingeConfig: Optional[HingeConfig]
            hinge data, null means hideHinge
    """
    return {
        "method": "Overlay.setShowHinge",
        "params": filter_none(
            {"hingeConfig": hingeConfig.to_json() if hingeConfig else None}
        ),
    }


@dataclasses.dataclass
class InspectNodeRequested:
    """Fired when the node should be inspected. This happens after call to `setInspectMode` or when
    user manually inspects an element.

    Attributes
    ----------
    backendNodeId: dom.BackendNodeId
            Id of the node to inspect.
    """

    backendNodeId: dom.BackendNodeId

    @classmethod
    def from_json(cls, json: dict) -> InspectNodeRequested:
        return cls(dom.BackendNodeId(json["backendNodeId"]))


@dataclasses.dataclass
class NodeHighlightRequested:
    """Fired when the node should be highlighted. This happens after call to `setInspectMode`.

    Attributes
    ----------
    nodeId: dom.NodeId
    """

    nodeId: dom.NodeId

    @classmethod
    def from_json(cls, json: dict) -> NodeHighlightRequested:
        return cls(dom.NodeId(json["nodeId"]))


@dataclasses.dataclass
class ScreenshotRequested:
    """Fired when user asks to capture screenshot of some area on the page.

    Attributes
    ----------
    viewport: page.Viewport
            Viewport to capture, in device independent pixels (dip).
    """

    viewport: page.Viewport

    @classmethod
    def from_json(cls, json: dict) -> ScreenshotRequested:
        return cls(page.Viewport.from_json(json["viewport"]))


@dataclasses.dataclass
class InspectModeCanceled:
    """Fired when user cancels the inspect mode."""

    @classmethod
    def from_json(cls, json: dict) -> InspectModeCanceled:
        return cls()
