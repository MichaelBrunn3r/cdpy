from __future__ import annotations

import dataclasses
import enum
from typing import Optional

from . import page
from .common import Type, filter_unset_parameters


@dataclasses.dataclass
class ApplicationCacheResource(Type):
    """Detailed application cache resource information.

    Attributes
    ----------
    url: str
            Resource url.
    size: int
            Resource size.
    type: str
            Resource type.
    """

    url: str
    size: int
    type: str

    @classmethod
    def from_json(cls, json: dict) -> ApplicationCacheResource:
        return cls(json["url"], json["size"], json["type"])


@dataclasses.dataclass
class ApplicationCache(Type):
    """Detailed application cache information.

    Attributes
    ----------
    manifestURL: str
            Manifest URL.
    size: float
            Application cache size.
    creationTime: float
            Application cache creation time.
    updateTime: float
            Application cache update time.
    resources: list[ApplicationCacheResource]
            Application cache resources.
    """

    manifestURL: str
    size: float
    creationTime: float
    updateTime: float
    resources: list[ApplicationCacheResource]

    @classmethod
    def from_json(cls, json: dict) -> ApplicationCache:
        return cls(
            json["manifestURL"],
            json["size"],
            json["creationTime"],
            json["updateTime"],
            [ApplicationCacheResource.from_json(x) for x in json["resources"]],
        )


@dataclasses.dataclass
class FrameWithManifest(Type):
    """Frame identifier - manifest URL pair.

    Attributes
    ----------
    frameId: page.FrameId
            Frame identifier.
    manifestURL: str
            Manifest URL.
    status: int
            Application cache status.
    """

    frameId: page.FrameId
    manifestURL: str
    status: int

    @classmethod
    def from_json(cls, json: dict) -> FrameWithManifest:
        return cls(page.FrameId(json["frameId"]), json["manifestURL"], json["status"])


def enable():
    """Enables application cache domain notifications."""
    return {"method": "ApplicationCache.enable", "params": {}}


def get_application_cache_for_frame(frameId: page.FrameId):
    """Returns relevant application cache data for the document in given frame.

    Parameters
    ----------
    frameId: page.FrameId
            Identifier of the frame containing document whose application cache is retrieved.

    Returns
    -------
    applicationCache: ApplicationCache
            Relevant application cache data for the document in given frame.
    """
    return {
        "method": "ApplicationCache.getApplicationCacheForFrame",
        "params": {"frameId": frameId},
    }


def get_frames_with_manifests():
    """Returns array of frame identifiers with manifest urls for each frame containing a document
    associated with some application cache.

    Returns
    -------
    frameIds: list[FrameWithManifest]
            Array of frame identifiers with manifest urls for each frame containing a document
            associated with some application cache.
    """
    return {"method": "ApplicationCache.getFramesWithManifests", "params": {}}


def get_manifest_for_frame(frameId: page.FrameId):
    """Returns manifest URL for document in the given frame.

    Parameters
    ----------
    frameId: page.FrameId
            Identifier of the frame containing document whose manifest is retrieved.

    Returns
    -------
    manifestURL: str
            Manifest URL for document in the given frame.
    """
    return {
        "method": "ApplicationCache.getManifestForFrame",
        "params": {"frameId": frameId},
    }