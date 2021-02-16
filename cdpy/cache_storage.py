from __future__ import annotations

import dataclasses
import enum
from typing import Generator, Optional

from .common import filter_none


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
class DataEntry:
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
            [Header.from_json(r) for r in json["requestHeaders"]],
            json["responseTime"],
            json["responseStatus"],
            json["responseStatusText"],
            CachedResponseType(json["responseType"]),
            [Header.from_json(r) for r in json["responseHeaders"]],
        )

    def to_json(self) -> dict:
        return {
            "requestURL": self.requestURL,
            "requestMethod": self.requestMethod,
            "requestHeaders": [r.to_json() for r in self.requestHeaders],
            "responseTime": self.responseTime,
            "responseStatus": self.responseStatus,
            "responseStatusText": self.responseStatusText,
            "responseType": self.responseType.value,
            "responseHeaders": [r.to_json() for r in self.responseHeaders],
        }


@dataclasses.dataclass
class Cache:
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

    def to_json(self) -> dict:
        return {
            "cacheId": str(self.cacheId),
            "securityOrigin": self.securityOrigin,
            "cacheName": self.cacheName,
        }


@dataclasses.dataclass
class Header:
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

    def to_json(self) -> dict:
        return {"name": self.name, "value": self.value}


@dataclasses.dataclass
class CachedResponse:
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

    def to_json(self) -> dict:
        return {"body": self.body}


def delete_cache(cacheId: CacheId) -> dict:
    """Deletes a cache.

    Parameters
    ----------
    cacheId: CacheId
            Id of cache for deletion.
    """
    return {"method": "CacheStorage.deleteCache", "params": {"cacheId": str(cacheId)}}


def delete_entry(cacheId: CacheId, request: str) -> dict:
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
        "params": {"cacheId": str(cacheId), "request": request},
    }


def request_cache_names(securityOrigin: str) -> Generator[dict, dict, list[Cache]]:
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
    response = yield {
        "method": "CacheStorage.requestCacheNames",
        "params": {"securityOrigin": securityOrigin},
    }
    return [Cache.from_json(c) for c in response["caches"]]


def request_cached_response(
    cacheId: CacheId, requestURL: str, requestHeaders: list[Header]
) -> Generator[dict, dict, CachedResponse]:
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
    response = yield {
        "method": "CacheStorage.requestCachedResponse",
        "params": {
            "cacheId": str(cacheId),
            "requestURL": requestURL,
            "requestHeaders": [r.to_json() for r in requestHeaders],
        },
    }
    return CachedResponse.from_json(response["response"])


def request_entries(
    cacheId: CacheId,
    skipCount: Optional[int] = None,
    pageSize: Optional[int] = None,
    pathFilter: Optional[str] = None,
) -> Generator[dict, dict, dict]:
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
    response = yield {
        "method": "CacheStorage.requestEntries",
        "params": filter_none(
            {
                "cacheId": str(cacheId),
                "skipCount": skipCount,
                "pageSize": pageSize,
                "pathFilter": pathFilter,
            }
        ),
    }
    return {
        "cacheDataEntries": [
            DataEntry.from_json(c) for c in response["cacheDataEntries"]
        ],
        "returnCount": response["returnCount"],
    }
