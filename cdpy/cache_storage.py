from __future__ import annotations

import dataclasses
import enum
from typing import Optional

from .common import Type, filter_unset_parameters


class CacheId(str):
    """Unique identifier of the Cache object."""

    def __repr__(self):
        return f"CacheId({super().__repr__()})"


class CachedResponseType(enum.Enum):
    """type of HTTP response cached"""

    BASIC = "basic"
    CORS = "cors"
    DEFAULT = "default"
    ERROR = "error"
    OPAQUE_RESPONSE = "opaqueResponse"
    OPAQUE_REDIRECT = "opaqueRedirect"


@dataclasses.dataclass
class DataEntry(Type):
    """Data entry.

    Attributes
    ----------
    requestURL: str
            Request URL.
    requestMethod: str
            Request method.
    requestHeaders: list[Header]
            Request headers
    responseTime: float
            Number of seconds since epoch.
    responseStatus: int
            HTTP response status code.
    responseStatusText: str
            HTTP response status text.
    responseType: CachedResponseType
            HTTP response type
    responseHeaders: list[Header]
            Response headers
    """

    requestURL: str
    requestMethod: str
    requestHeaders: list[Header]
    responseTime: float
    responseStatus: int
    responseStatusText: str
    responseType: CachedResponseType
    responseHeaders: list[Header]

    @classmethod
    def from_json(cls, json: dict) -> DataEntry:
        return cls(
            json["requestURL"],
            json["requestMethod"],
            [Header.from_json(x) for x in json["requestHeaders"]],
            json["responseTime"],
            json["responseStatus"],
            json["responseStatusText"],
            CachedResponseType(json["responseType"]),
            [Header.from_json(x) for x in json["responseHeaders"]],
        )


@dataclasses.dataclass
class Cache(Type):
    """Cache identifier.

    Attributes
    ----------
    cacheId: CacheId
            An opaque unique id of the cache.
    securityOrigin: str
            Security origin of the cache.
    cacheName: str
            The name of the cache.
    """

    cacheId: CacheId
    securityOrigin: str
    cacheName: str

    @classmethod
    def from_json(cls, json: dict) -> Cache:
        return cls(CacheId(json["cacheId"]), json["securityOrigin"], json["cacheName"])


@dataclasses.dataclass
class Header(Type):
    """
    Attributes
    ----------
    name: str
    value: str
    """

    name: str
    value: str

    @classmethod
    def from_json(cls, json: dict) -> Header:
        return cls(json["name"], json["value"])


@dataclasses.dataclass
class CachedResponse(Type):
    """Cached response

    Attributes
    ----------
    body: str
            Entry content, base64-encoded. (Encoded as a base64 string when passed over JSON)
    """

    body: str

    @classmethod
    def from_json(cls, json: dict) -> CachedResponse:
        return cls(json["body"])


def delete_cache(cacheId: CacheId):
    """Deletes a cache.

    Parameters
    ----------
    cacheId: CacheId
            Id of cache for deletion.
    """
    return {"method": "CacheStorage.deleteCache", "params": {"cacheId": cacheId}}


def delete_entry(cacheId: CacheId, request: str):
    """Deletes a cache entry.

    Parameters
    ----------
    cacheId: CacheId
            Id of cache where the entry will be deleted.
    request: str
            URL spec of the request.
    """
    return {
        "method": "CacheStorage.deleteEntry",
        "params": {"cacheId": cacheId, "request": request},
    }


def request_cache_names(securityOrigin: str):
    """Requests cache names.

    Parameters
    ----------
    securityOrigin: str
            Security origin.

    Returns
    -------
    caches: list[Cache]
            Caches for the security origin.
    """
    return {
        "method": "CacheStorage.requestCacheNames",
        "params": {"securityOrigin": securityOrigin},
    }


def request_cached_response(
    cacheId: CacheId, requestURL: str, requestHeaders: list[Header]
):
    """Fetches cache entry.

    Parameters
    ----------
    cacheId: CacheId
            Id of cache that contains the entry.
    requestURL: str
            URL spec of the request.
    requestHeaders: list[Header]
            headers of the request.

    Returns
    -------
    response: CachedResponse
            Response read from the cache.
    """
    return {
        "method": "CacheStorage.requestCachedResponse",
        "params": {
            "cacheId": cacheId,
            "requestURL": requestURL,
            "requestHeaders": requestHeaders,
        },
    }


def request_entries(
    cacheId: CacheId,
    skipCount: Optional[int] = None,
    pageSize: Optional[int] = None,
    pathFilter: Optional[str] = None,
):
    """Requests data from cache.

    Parameters
    ----------
    cacheId: CacheId
            ID of cache to get entries from.
    skipCount: Optional[int]
            Number of records to skip.
    pageSize: Optional[int]
            Number of records to fetch.
    pathFilter: Optional[str]
            If present, only return the entries containing this substring in the path

    Returns
    -------
    cacheDataEntries: list[DataEntry]
            Array of object store data entries.
    returnCount: float
            Count of returned entries from this storage. If pathFilter is empty, it
            is the count of all entries from this storage.
    """
    return filter_unset_parameters(
        {
            "method": "CacheStorage.requestEntries",
            "params": {
                "cacheId": cacheId,
                "skipCount": skipCount,
                "pageSize": pageSize,
                "pathFilter": pathFilter,
            },
        }
    )