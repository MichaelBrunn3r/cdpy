from __future__ import annotations

import dataclasses
import enum
from typing import Optional

from . import dom, page, runtime
from .common import Type, filter_unset_parameters


@dataclasses.dataclass
class SourceOrderConfig(Type):
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


@dataclasses.dataclass
class GridHighlightConfig(Type):
    """Configuration data for the highlighting of Grid elements.

    Attributes
    ----------
    showGridExtensionLines: Optional[bool] = None
            Whether the extension lines from grid cells to the rulers should be shown (default: false).
    showPositiveLineNumbers: Optional[bool] = None
            Show Positive line number labels (default: false).
    showNegativeLineNumbers: Optional[bool] = None
            Show Negative line number labels (default: false).
    showAreaNames: Optional[bool] = None
            Show area name labels (default: false).
    showLineNames: Optional[bool] = None
            Show line name labels (default: false).
    showTrackSizes: Optional[bool] = None
            Show track size labels (default: false).
    gridBorderColor: Optional[dom.RGBA] = None
            The grid container border highlight color (default: transparent).
    cellBorderColor: Optional[dom.RGBA] = None
            The cell border color (default: transparent). Deprecated, please use rowLineColor and columnLineColor instead.
    rowLineColor: Optional[dom.RGBA] = None
            The row line color (default: transparent).
    columnLineColor: Optional[dom.RGBA] = None
            The column line color (default: transparent).
    gridBorderDash: Optional[bool] = None
            Whether the grid border is dashed (default: false).
    cellBorderDash: Optional[bool] = None
            Whether the cell border is dashed (default: false). Deprecated, please us rowLineDash and columnLineDash instead.
    rowLineDash: Optional[bool] = None
            Whether row lines are dashed (default: false).
    columnLineDash: Optional[bool] = None
            Whether column lines are dashed (default: false).
    rowGapColor: Optional[dom.RGBA] = None
            The row gap highlight fill color (default: transparent).
    rowHatchColor: Optional[dom.RGBA] = None
            The row gap hatching fill color (default: transparent).
    columnGapColor: Optional[dom.RGBA] = None
            The column gap highlight fill color (default: transparent).
    columnHatchColor: Optional[dom.RGBA] = None
            The column gap hatching fill color (default: transparent).
    areaBorderColor: Optional[dom.RGBA] = None
            The named grid areas border color (Default: transparent).
    gridBackgroundColor: Optional[dom.RGBA] = None
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


@dataclasses.dataclass
class FlexContainerHighlightConfig(Type):
    """Configuration data for the highlighting of Flex container elements.

    Attributes
    ----------
    containerBorder: Optional[LineStyle] = None
            The style of the container border
    lineSeparator: Optional[LineStyle] = None
            The style of the separator between lines
    itemSeparator: Optional[LineStyle] = None
            The style of the separator between items
    mainDistributedSpace: Optional[BoxStyle] = None
            Style of content-distribution space on the main axis (justify-content).
    crossDistributedSpace: Optional[BoxStyle] = None
            Style of content-distribution space on the cross axis (align-content).
    rowGapSpace: Optional[BoxStyle] = None
            Style of empty space caused by row gaps (gap/row-gap).
    columnGapSpace: Optional[BoxStyle] = None
            Style of empty space caused by columns gaps (gap/column-gap).
    crossAlignment: Optional[LineStyle] = None
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


@dataclasses.dataclass
class FlexItemHighlightConfig(Type):
    """Configuration data for the highlighting of Flex item elements.

    Attributes
    ----------
    baseSizeBox: Optional[BoxStyle] = None
            Style of the box representing the item's base size
    baseSizeBorder: Optional[LineStyle] = None
            Style of the border around the box representing the item's base size
    flexibilityArrow: Optional[LineStyle] = None
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


@dataclasses.dataclass
class LineStyle(Type):
    """Style information for drawing a line.

    Attributes
    ----------
    color: Optional[dom.RGBA] = None
            The color of the line (default: transparent)
    pattern: Optional[str] = None
            The line pattern (default: solid)
    """

    color: Optional[dom.RGBA] = None
    pattern: Optional[str] = None

    @classmethod
    def from_json(cls, json: dict) -> LineStyle:
        return cls(dom.RGBA.from_json(json["color"]) if "color" in json else None)


@dataclasses.dataclass
class BoxStyle(Type):
    """Style information for drawing a box.

    Attributes
    ----------
    fillColor: Optional[dom.RGBA] = None
            The background color for the box (default: transparent)
    hatchColor: Optional[dom.RGBA] = None
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


class ContrastAlgorithm(enum.Enum):
    """"""

    AA = "aa"
    AAA = "aaa"
    APCA = "apca"


@dataclasses.dataclass
class HighlightConfig(Type):
    """Configuration data for the highlighting of page elements.

    Attributes
    ----------
    showInfo: Optional[bool] = None
            Whether the node info tooltip should be shown (default: false).
    showStyles: Optional[bool] = None
            Whether the node styles in the tooltip (default: false).
    showRulers: Optional[bool] = None
            Whether the rulers should be shown (default: false).
    showAccessibilityInfo: Optional[bool] = None
            Whether the a11y info should be shown (default: true).
    showExtensionLines: Optional[bool] = None
            Whether the extension lines from node to the rulers should be shown (default: false).
    contentColor: Optional[dom.RGBA] = None
            The content box highlight fill color (default: transparent).
    paddingColor: Optional[dom.RGBA] = None
            The padding highlight fill color (default: transparent).
    borderColor: Optional[dom.RGBA] = None
            The border highlight fill color (default: transparent).
    marginColor: Optional[dom.RGBA] = None
            The margin highlight fill color (default: transparent).
    eventTargetColor: Optional[dom.RGBA] = None
            The event target element highlight fill color (default: transparent).
    shapeColor: Optional[dom.RGBA] = None
            The shape outside fill color (default: transparent).
    shapeMarginColor: Optional[dom.RGBA] = None
            The shape margin fill color (default: transparent).
    cssGridColor: Optional[dom.RGBA] = None
            The grid layout color (default: transparent).
    colorFormat: Optional[ColorFormat] = None
            The color format used to format color styles (default: hex).
    gridHighlightConfig: Optional[GridHighlightConfig] = None
            The grid layout highlight configuration (default: all transparent).
    flexContainerHighlightConfig: Optional[FlexContainerHighlightConfig] = None
            The flex container highlight configuration (default: all transparent).
    flexItemHighlightConfig: Optional[FlexItemHighlightConfig] = None
            The flex item highlight configuration (default: all transparent).
    contrastAlgorithm: Optional[ContrastAlgorithm] = None
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


class ColorFormat(enum.Enum):
    """"""

    RGB = "rgb"
    HSL = "hsl"
    HEX = "hex"


@dataclasses.dataclass
class GridNodeHighlightConfig(Type):
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


@dataclasses.dataclass
class FlexNodeHighlightConfig(Type):
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


@dataclasses.dataclass
class HingeConfig(Type):
    """Configuration for dual screen hinge

    Attributes
    ----------
    rect: dom.Rect
            A rectangle represent hinge
    contentColor: Optional[dom.RGBA] = None
            The content box highlight fill color (default: a dark color).
    outlineColor: Optional[dom.RGBA] = None
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


class InspectMode(enum.Enum):
    """"""

    SEARCH_FOR_NODE = "searchForNode"
    SEARCH_FOR_UA_SHADOW_DOM = "searchForUAShadowDOM"
    CAPTURE_AREA_SCREENSHOT = "captureAreaScreenshot"
    SHOW_DISTANCES = "showDistances"
    NONE = "none"


def disable():
    """Disables domain notifications."""
    return {"method": "Overlay.disable", "params": {}}


def enable():
    """Enables domain notifications."""
    return {"method": "Overlay.enable", "params": {}}


def get_highlight_object_for_test(
    nodeId: dom.NodeId,
    includeDistance: Optional[bool] = None,
    includeStyle: Optional[bool] = None,
    colorFormat: Optional[ColorFormat] = None,
    showAccessibilityInfo: Optional[bool] = None,
):
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
    return filter_unset_parameters(
        {
            "method": "Overlay.getHighlightObjectForTest",
            "params": {
                "nodeId": nodeId,
                "includeDistance": includeDistance,
                "includeStyle": includeStyle,
                "colorFormat": colorFormat,
                "showAccessibilityInfo": showAccessibilityInfo,
            },
        }
    )


def get_grid_highlight_objects_for_test(nodeIds: list[dom.NodeId]):
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
    return {
        "method": "Overlay.getGridHighlightObjectsForTest",
        "params": {"nodeIds": nodeIds},
    }


def get_source_order_highlight_object_for_test(nodeId: dom.NodeId):
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
    return {
        "method": "Overlay.getSourceOrderHighlightObjectForTest",
        "params": {"nodeId": nodeId},
    }


def hide_highlight():
    """Hides any highlight."""
    return {"method": "Overlay.hideHighlight", "params": {}}


def highlight_frame(
    frameId: page.FrameId,
    contentColor: Optional[dom.RGBA] = None,
    contentOutlineColor: Optional[dom.RGBA] = None,
):
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
    return filter_unset_parameters(
        {
            "method": "Overlay.highlightFrame",
            "params": {
                "frameId": frameId,
                "contentColor": contentColor,
                "contentOutlineColor": contentOutlineColor,
            },
        }
    )


def highlight_node(
    highlightConfig: HighlightConfig,
    nodeId: Optional[dom.NodeId] = None,
    backendNodeId: Optional[dom.BackendNodeId] = None,
    objectId: Optional[runtime.RemoteObjectId] = None,
    selector: Optional[str] = None,
):
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
    return filter_unset_parameters(
        {
            "method": "Overlay.highlightNode",
            "params": {
                "highlightConfig": highlightConfig,
                "nodeId": nodeId,
                "backendNodeId": backendNodeId,
                "objectId": objectId,
                "selector": selector,
            },
        }
    )


def highlight_quad(
    quad: dom.Quad,
    color: Optional[dom.RGBA] = None,
    outlineColor: Optional[dom.RGBA] = None,
):
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
    return filter_unset_parameters(
        {
            "method": "Overlay.highlightQuad",
            "params": {"quad": quad, "color": color, "outlineColor": outlineColor},
        }
    )


def highlight_rect(
    x: int,
    y: int,
    width: int,
    height: int,
    color: Optional[dom.RGBA] = None,
    outlineColor: Optional[dom.RGBA] = None,
):
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
    return filter_unset_parameters(
        {
            "method": "Overlay.highlightRect",
            "params": {
                "x": x,
                "y": y,
                "width": width,
                "height": height,
                "color": color,
                "outlineColor": outlineColor,
            },
        }
    )


def highlight_source_order(
    sourceOrderConfig: SourceOrderConfig,
    nodeId: Optional[dom.NodeId] = None,
    backendNodeId: Optional[dom.BackendNodeId] = None,
    objectId: Optional[runtime.RemoteObjectId] = None,
):
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
    return filter_unset_parameters(
        {
            "method": "Overlay.highlightSourceOrder",
            "params": {
                "sourceOrderConfig": sourceOrderConfig,
                "nodeId": nodeId,
                "backendNodeId": backendNodeId,
                "objectId": objectId,
            },
        }
    )


def set_inspect_mode(
    mode: InspectMode, highlightConfig: Optional[HighlightConfig] = None
):
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
    return filter_unset_parameters(
        {
            "method": "Overlay.setInspectMode",
            "params": {"mode": mode, "highlightConfig": highlightConfig},
        }
    )


def set_show_ad_highlights(show: bool):
    """Highlights owner element of all frames detected to be ads.

    Parameters
    ----------
    show: bool
            True for showing ad highlights
    """
    return {"method": "Overlay.setShowAdHighlights", "params": {"show": show}}


def set_paused_in_debugger_message(message: Optional[str] = None):
    """
    Parameters
    ----------
    message: Optional[str]
            The message to display, also triggers resume and step over controls.
    """
    return filter_unset_parameters(
        {"method": "Overlay.setPausedInDebuggerMessage", "params": {"message": message}}
    )


def set_show_debug_borders(show: bool):
    """Requests that backend shows debug borders on layers

    Parameters
    ----------
    show: bool
            True for showing debug borders
    """
    return {"method": "Overlay.setShowDebugBorders", "params": {"show": show}}


def set_show_fps_counter(show: bool):
    """Requests that backend shows the FPS counter

    Parameters
    ----------
    show: bool
            True for showing the FPS counter
    """
    return {"method": "Overlay.setShowFPSCounter", "params": {"show": show}}


def set_show_grid_overlays(gridNodeHighlightConfigs: list[GridNodeHighlightConfig]):
    """Highlight multiple elements with the CSS Grid overlay.

    Parameters
    ----------
    gridNodeHighlightConfigs: list[GridNodeHighlightConfig]
            An array of node identifiers and descriptors for the highlight appearance.
    """
    return {
        "method": "Overlay.setShowGridOverlays",
        "params": {"gridNodeHighlightConfigs": gridNodeHighlightConfigs},
    }


def set_show_flex_overlays(flexNodeHighlightConfigs: list[FlexNodeHighlightConfig]):
    """
    Parameters
    ----------
    flexNodeHighlightConfigs: list[FlexNodeHighlightConfig]
            An array of node identifiers and descriptors for the highlight appearance.
    """
    return {
        "method": "Overlay.setShowFlexOverlays",
        "params": {"flexNodeHighlightConfigs": flexNodeHighlightConfigs},
    }


def set_show_paint_rects(result: bool):
    """Requests that backend shows paint rectangles

    Parameters
    ----------
    result: bool
            True for showing paint rectangles
    """
    return {"method": "Overlay.setShowPaintRects", "params": {"result": result}}


def set_show_layout_shift_regions(result: bool):
    """Requests that backend shows layout shift regions

    Parameters
    ----------
    result: bool
            True for showing layout shift regions
    """
    return {"method": "Overlay.setShowLayoutShiftRegions", "params": {"result": result}}


def set_show_scroll_bottleneck_rects(show: bool):
    """Requests that backend shows scroll bottleneck rects

    Parameters
    ----------
    show: bool
            True for showing scroll bottleneck rects
    """
    return {"method": "Overlay.setShowScrollBottleneckRects", "params": {"show": show}}


def set_show_hit_test_borders(show: bool):
    """Requests that backend shows hit-test borders on layers

    Parameters
    ----------
    show: bool
            True for showing hit-test borders
    """
    return {"method": "Overlay.setShowHitTestBorders", "params": {"show": show}}


def set_show_web_vitals(show: bool):
    """Request that backend shows an overlay with web vital metrics.

    Parameters
    ----------
    show: bool
    """
    return {"method": "Overlay.setShowWebVitals", "params": {"show": show}}


def set_show_viewport_size_on_resize(show: bool):
    """Paints viewport size upon main frame resize.

    Parameters
    ----------
    show: bool
            Whether to paint size or not.
    """
    return {"method": "Overlay.setShowViewportSizeOnResize", "params": {"show": show}}


def set_show_hinge(hingeConfig: Optional[HingeConfig] = None):
    """Add a dual screen device hinge

    Parameters
    ----------
    hingeConfig: Optional[HingeConfig]
            hinge data, null means hideHinge
    """
    return filter_unset_parameters(
        {"method": "Overlay.setShowHinge", "params": {"hingeConfig": hingeConfig}}
    )