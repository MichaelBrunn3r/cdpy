from __future__ import annotations

import dataclasses
import enum
from typing import Optional

from . import browser, network
from .common import Type, filter_unset_parameters


class StorageType(enum.Enum):
    """Enum of possible storage types."""

    APPCACHE = "appcache"
    COOKIES = "cookies"
    FILE_SYSTEMS = "file_systems"
    INDEXEDDB = "indexeddb"
    LOCAL_STORAGE = "local_storage"
    SHADER_CACHE = "shader_cache"
    WEBSQL = "websql"
    SERVICE_WORKERS = "service_workers"
    CACHE_STORAGE = "cache_storage"
    ALL = "all"
    OTHER = "other"


@dataclasses.dataclass
class UsageForType(Type):
    """Usage for a storage type.

    Attributes
    ----------
    storageType: StorageType
            Name of storage type.
    usage: float
            Storage usage (bytes).
    """

    storageType: StorageType
    usage: float

    @classmethod
    def from_json(cls, json: dict) -> UsageForType:
        return cls(StorageType(json["storageType"]), json["usage"])


@dataclasses.dataclass
class TrustTokens(Type):
    """Pair of issuer origin and number of available (signed, but not used) Trust
    Tokens from that issuer.

    Attributes
    ----------
    issuerOrigin: str
    count: float
    """

    issuerOrigin: str
    count: float

    @classmethod
    def from_json(cls, json: dict) -> TrustTokens:
        return cls(json["issuerOrigin"], json["count"])


def clear_data_for_origin(origin: str, storageTypes: str):
    """Clears storage for origin.

    Parameters
    ----------
    origin: str
            Security origin.
    storageTypes: str
            Comma separated list of StorageType to clear.
    """
    return {
        "method": "Storage.clearDataForOrigin",
        "params": {"origin": origin, "storageTypes": storageTypes},
    }


def get_cookies(browserContextId: Optional[browser.BrowserContextID] = None):
    """Returns all browser cookies.

    Parameters
    ----------
    browserContextId: Optional[browser.BrowserContextID]
            Browser context to use when called on the browser endpoint.

    Returns
    -------
    cookies: list[network.Cookie]
            Array of cookie objects.
    """
    return filter_unset_parameters(
        {
            "method": "Storage.getCookies",
            "params": {"browserContextId": browserContextId},
        }
    )


def set_cookies(
    cookies: list[network.CookieParam],
    browserContextId: Optional[browser.BrowserContextID] = None,
):
    """Sets given cookies.

    Parameters
    ----------
    cookies: list[network.CookieParam]
            Cookies to be set.
    browserContextId: Optional[browser.BrowserContextID]
            Browser context to use when called on the browser endpoint.
    """
    return filter_unset_parameters(
        {
            "method": "Storage.setCookies",
            "params": {"cookies": cookies, "browserContextId": browserContextId},
        }
    )


def clear_cookies(browserContextId: Optional[browser.BrowserContextID] = None):
    """Clears cookies.

    Parameters
    ----------
    browserContextId: Optional[browser.BrowserContextID]
            Browser context to use when called on the browser endpoint.
    """
    return filter_unset_parameters(
        {
            "method": "Storage.clearCookies",
            "params": {"browserContextId": browserContextId},
        }
    )


def get_usage_and_quota(origin: str):
    """Returns usage and quota in bytes.

    Parameters
    ----------
    origin: str
            Security origin.

    Returns
    -------
    usage: float
            Storage usage (bytes).
    quota: float
            Storage quota (bytes).
    overrideActive: bool
            Whether or not the origin has an active storage quota override
    usageBreakdown: list[UsageForType]
            Storage usage per type (bytes).
    """
    return {"method": "Storage.getUsageAndQuota", "params": {"origin": origin}}


def override_quota_for_origin(origin: str, quotaSize: Optional[float] = None):
    """Override quota for the specified origin

    **Experimental**

    Parameters
    ----------
    origin: str
            Security origin.
    quotaSize: Optional[float]
            The quota size (in bytes) to override the original quota with.
            If this is called multiple times, the overriden quota will be equal to
            the quotaSize provided in the final call. If this is called without
            specifying a quotaSize, the quota will be reset to the default value for
            the specified origin. If this is called multiple times with different
            origins, the override will be maintained for each origin until it is
            disabled (called without a quotaSize).
    """
    return filter_unset_parameters(
        {
            "method": "Storage.overrideQuotaForOrigin",
            "params": {"origin": origin, "quotaSize": quotaSize},
        }
    )


def track_cache_storage_for_origin(origin: str):
    """Registers origin to be notified when an update occurs to its cache storage list.

    Parameters
    ----------
    origin: str
            Security origin.
    """
    return {
        "method": "Storage.trackCacheStorageForOrigin",
        "params": {"origin": origin},
    }


def track_indexed_db_for_origin(origin: str):
    """Registers origin to be notified when an update occurs to its IndexedDB.

    Parameters
    ----------
    origin: str
            Security origin.
    """
    return {"method": "Storage.trackIndexedDBForOrigin", "params": {"origin": origin}}


def untrack_cache_storage_for_origin(origin: str):
    """Unregisters origin from receiving notifications for cache storage.

    Parameters
    ----------
    origin: str
            Security origin.
    """
    return {
        "method": "Storage.untrackCacheStorageForOrigin",
        "params": {"origin": origin},
    }


def untrack_indexed_db_for_origin(origin: str):
    """Unregisters origin from receiving notifications for IndexedDB.

    Parameters
    ----------
    origin: str
            Security origin.
    """
    return {"method": "Storage.untrackIndexedDBForOrigin", "params": {"origin": origin}}


def get_trust_tokens():
    """Returns the number of stored Trust Tokens per issuer for the
    current browsing context.

    **Experimental**

    Returns
    -------
    tokens: list[TrustTokens]
    """
    return {"method": "Storage.getTrustTokens", "params": {}}
