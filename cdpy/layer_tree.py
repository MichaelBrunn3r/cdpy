from __future__ import annotations

import dataclasses
from typing import Generator, Optional

from . import dom
from .common import filter_none, filter_unset_parameters


class LayerId(str):
    """Unique Layer identifier."""

    def __repr__(self):
        return f"LayerId({super().__repr__()})"


class SnapshotId(str):
    """Unique snapshot identifier."""

    def __repr__(self):
        return f"SnapshotId({super().__repr__()})"


@dataclasses.dataclass
class ScrollRect:
    """Rectangle where scrolling happens on the main thread.

    Attributes
    ----------
    rect: dom.Rect
            Rectangle itself.
    type: str
            Reason for rectangle to force scrolling on the main thread
    """

    rect: dom.Rect
    type: str

    @classmethod
    def from_json(cls, json: dict) -> ScrollRect:
        return cls(dom.Rect.from_json(json["rect"]), json["type"])

    def to_json(self) -> dict:
        return {"rect": self.rect.to_json(), "type": self.type}


@dataclasses.dataclass
class StickyPositionConstraint:
    """Sticky position constraints.

    Attributes
    ----------
    stickyBoxRect: dom.Rect
            Layout rectangle of the sticky element before being shifted
    containingBlockRect: dom.Rect
            Layout rectangle of the containing block of the sticky element
    nearestLayerShiftingStickyBox: Optional[LayerId]
            The nearest sticky layer that shifts the sticky box
    nearestLayerShiftingContainingBlock: Optional[LayerId]
            The nearest sticky layer that shifts the containing block
    """

    stickyBoxRect: dom.Rect
    containingBlockRect: dom.Rect
    nearestLayerShiftingStickyBox: Optional[LayerId] = None
    nearestLayerShiftingContainingBlock: Optional[LayerId] = None

    @classmethod
    def from_json(cls, json: dict) -> StickyPositionConstraint:
        return cls(
            dom.Rect.from_json(json["stickyBoxRect"]),
            dom.Rect.from_json(json["containingBlockRect"]),
            LayerId(json["nearestLayerShiftingStickyBox"])
            if "nearestLayerShiftingStickyBox" in json
            else None,
            LayerId(json["nearestLayerShiftingContainingBlock"])
            if "nearestLayerShiftingContainingBlock" in json
            else None,
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "stickyBoxRect": self.stickyBoxRect.to_json(),
                "containingBlockRect": self.containingBlockRect.to_json(),
                "nearestLayerShiftingStickyBox": str(self.nearestLayerShiftingStickyBox)
                if self.nearestLayerShiftingStickyBox
                else None,
                "nearestLayerShiftingContainingBlock": str(
                    self.nearestLayerShiftingContainingBlock
                )
                if self.nearestLayerShiftingContainingBlock
                else None,
            }
        )


@dataclasses.dataclass
class PictureTile:
    """Serialized fragment of layer picture along with its offset within the layer.

    Attributes
    ----------
    x: float
            Offset from owning layer left boundary
    y: float
            Offset from owning layer top boundary
    picture: str
            Base64-encoded snapshot data. (Encoded as a base64 string when passed over JSON)
    """

    x: float
    y: float
    picture: str

    @classmethod
    def from_json(cls, json: dict) -> PictureTile:
        return cls(json["x"], json["y"], json["picture"])

    def to_json(self) -> dict:
        return {"x": self.x, "y": self.y, "picture": self.picture}


@dataclasses.dataclass
class Layer:
    """Information about a compositing layer.

    Attributes
    ----------
    layerId: LayerId
            The unique id for this layer.
    offsetX: float
            Offset from parent layer, X coordinate.
    offsetY: float
            Offset from parent layer, Y coordinate.
    width: float
            Layer width.
    height: float
            Layer height.
    paintCount: int
            Indicates how many time this layer has painted.
    drawsContent: bool
            Indicates whether this layer hosts any content, rather than being used for
            transform/scrolling purposes only.
    parentLayerId: Optional[LayerId]
            The id of parent (not present for root).
    backendNodeId: Optional[dom.BackendNodeId]
            The backend id for the node associated with this layer.
    transform: Optional[list[float]]
            Transformation matrix for layer, default is identity matrix
    anchorX: Optional[float]
            Transform anchor point X, absent if no transform specified
    anchorY: Optional[float]
            Transform anchor point Y, absent if no transform specified
    anchorZ: Optional[float]
            Transform anchor point Z, absent if no transform specified
    invisible: Optional[bool]
            Set if layer is not visible.
    scrollRects: Optional[list[ScrollRect]]
            Rectangles scrolling on main thread only.
    stickyPositionConstraint: Optional[StickyPositionConstraint]
            Sticky position constraint information
    """

    layerId: LayerId
    offsetX: float
    offsetY: float
    width: float
    height: float
    paintCount: int
    drawsContent: bool
    parentLayerId: Optional[LayerId] = None
    backendNodeId: Optional[dom.BackendNodeId] = None
    transform: Optional[list[float]] = None
    anchorX: Optional[float] = None
    anchorY: Optional[float] = None
    anchorZ: Optional[float] = None
    invisible: Optional[bool] = None
    scrollRects: Optional[list[ScrollRect]] = None
    stickyPositionConstraint: Optional[StickyPositionConstraint] = None

    @classmethod
    def from_json(cls, json: dict) -> Layer:
        return cls(
            LayerId(json["layerId"]),
            json["offsetX"],
            json["offsetY"],
            json["width"],
            json["height"],
            json["paintCount"],
            json["drawsContent"],
            LayerId(json["parentLayerId"]) if "parentLayerId" in json else None,
            dom.BackendNodeId(json["backendNodeId"])
            if "backendNodeId" in json
            else None,
            json.get("transform"),
            json.get("anchorX"),
            json.get("anchorY"),
            json.get("anchorZ"),
            json.get("invisible"),
            [ScrollRect.from_json(s) for s in json["scrollRects"]]
            if "scrollRects" in json
            else None,
            StickyPositionConstraint.from_json(json["stickyPositionConstraint"])
            if "stickyPositionConstraint" in json
            else None,
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "layerId": str(self.layerId),
                "offsetX": self.offsetX,
                "offsetY": self.offsetY,
                "width": self.width,
                "height": self.height,
                "paintCount": self.paintCount,
                "drawsContent": self.drawsContent,
                "parentLayerId": str(self.parentLayerId)
                if self.parentLayerId
                else None,
                "backendNodeId": int(self.backendNodeId)
                if self.backendNodeId
                else None,
                "transform": self.transform,
                "anchorX": self.anchorX,
                "anchorY": self.anchorY,
                "anchorZ": self.anchorZ,
                "invisible": self.invisible,
                "scrollRects": [s.to_json() for s in self.scrollRects]
                if self.scrollRects
                else None,
                "stickyPositionConstraint": self.stickyPositionConstraint.to_json()
                if self.stickyPositionConstraint
                else None,
            }
        )


class PaintProfile(list[float]):
    """Array of timings, one per paint step."""

    def __repr__(self):
        return f"PaintProfile({super().__repr__()})"


def compositing_reasons(layerId: LayerId) -> Generator[dict, dict, dict]:
    """Provides the reasons why the given layer was composited.

    Parameters
    ----------
    layerId: LayerId
            The id of the layer for which we want to get the reasons it was composited.

    Returns
    -------
    compositingReasons: list[str]
            A list of strings specifying reasons for the given layer to become composited.
    compositingReasonIds: list[str]
            A list of strings specifying reason IDs for the given layer to become composited.
    """
    response = yield {
        "method": "LayerTree.compositingReasons",
        "params": {"layerId": layerId},
    }
    return {
        "compositingReasons": response["compositingReasons"],
        "compositingReasonIds": response["compositingReasonIds"],
    }


def disable() -> dict:
    """Disables compositing tree inspection."""
    return {"method": "LayerTree.disable", "params": {}}


def enable() -> dict:
    """Enables compositing tree inspection."""
    return {"method": "LayerTree.enable", "params": {}}


def load_snapshot(tiles: list[PictureTile]) -> Generator[dict, dict, SnapshotId]:
    """Returns the snapshot identifier.

    Parameters
    ----------
    tiles: list[PictureTile]
            An array of tiles composing the snapshot.

    Returns
    -------
    snapshotId: SnapshotId
            The id of the snapshot.
    """
    response = yield {"method": "LayerTree.loadSnapshot", "params": {"tiles": tiles}}
    return SnapshotId(response)


def make_snapshot(layerId: LayerId) -> Generator[dict, dict, SnapshotId]:
    """Returns the layer snapshot identifier.

    Parameters
    ----------
    layerId: LayerId
            The id of the layer.

    Returns
    -------
    snapshotId: SnapshotId
            The id of the layer snapshot.
    """
    response = yield {
        "method": "LayerTree.makeSnapshot",
        "params": {"layerId": layerId},
    }
    return SnapshotId(response)


def profile_snapshot(
    snapshotId: SnapshotId,
    minRepeatCount: Optional[int] = None,
    minDuration: Optional[float] = None,
    clipRect: Optional[dom.Rect] = None,
) -> Generator[dict, dict, list[PaintProfile]]:
    """
    Parameters
    ----------
    snapshotId: SnapshotId
            The id of the layer snapshot.
    minRepeatCount: Optional[int]
            The maximum number of times to replay the snapshot (1, if not specified).
    minDuration: Optional[float]
            The minimum duration (in seconds) to replay the snapshot.
    clipRect: Optional[dom.Rect]
            The clip rectangle to apply when replaying the snapshot.

    Returns
    -------
    timings: list[PaintProfile]
            The array of paint profiles, one per run.
    """
    response = yield filter_unset_parameters(
        {
            "method": "LayerTree.profileSnapshot",
            "params": {
                "snapshotId": snapshotId,
                "minRepeatCount": minRepeatCount,
                "minDuration": minDuration,
                "clipRect": clipRect,
            },
        }
    )
    return [PaintProfile(t) for t in response]


def release_snapshot(snapshotId: SnapshotId) -> dict:
    """Releases layer snapshot captured by the back-end.

    Parameters
    ----------
    snapshotId: SnapshotId
            The id of the layer snapshot.
    """
    return {"method": "LayerTree.releaseSnapshot", "params": {"snapshotId": snapshotId}}


def replay_snapshot(
    snapshotId: SnapshotId,
    fromStep: Optional[int] = None,
    toStep: Optional[int] = None,
    scale: Optional[float] = None,
) -> Generator[dict, dict, str]:
    """Replays the layer snapshot and returns the resulting bitmap.

    Parameters
    ----------
    snapshotId: SnapshotId
            The id of the layer snapshot.
    fromStep: Optional[int]
            The first step to replay from (replay from the very start if not specified).
    toStep: Optional[int]
            The last step to replay to (replay till the end if not specified).
    scale: Optional[float]
            The scale to apply while replaying (defaults to 1).

    Returns
    -------
    dataURL: str
            A data: URL for resulting image.
    """
    response = yield filter_unset_parameters(
        {
            "method": "LayerTree.replaySnapshot",
            "params": {
                "snapshotId": snapshotId,
                "fromStep": fromStep,
                "toStep": toStep,
                "scale": scale,
            },
        }
    )
    return response


def snapshot_command_log(snapshotId: SnapshotId) -> Generator[dict, dict, list[dict]]:
    """Replays the layer snapshot and returns canvas log.

    Parameters
    ----------
    snapshotId: SnapshotId
            The id of the layer snapshot.

    Returns
    -------
    commandLog: list[dict]
            The array of canvas function calls.
    """
    response = yield {
        "method": "LayerTree.snapshotCommandLog",
        "params": {"snapshotId": snapshotId},
    }
    return response
