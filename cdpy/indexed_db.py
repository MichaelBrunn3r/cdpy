from __future__ import annotations

import dataclasses
import enum
from typing import Optional

from . import runtime
from .common import Type, filter_unset_parameters


@dataclasses.dataclass
class DatabaseWithObjectStores(Type):
    """Database with an array of object stores.

    Attributes
    ----------
    name: str
            Database name.
    version: float
            Database version (type is not 'integer', as the standard
            requires the version number to be 'unsigned long long')
    objectStores: list[ObjectStore]
            Object stores in this database.
    """

    name: str
    version: float
    objectStores: list[ObjectStore]

    @classmethod
    def from_json(cls, json: dict) -> DatabaseWithObjectStores:
        return cls(
            json["name"],
            json["version"],
            [ObjectStore.from_json(x) for x in json["objectStores"]],
        )


@dataclasses.dataclass
class ObjectStore(Type):
    """Object store.

    Attributes
    ----------
    name: str
            Object store name.
    keyPath: KeyPath
            Object store key path.
    autoIncrement: bool
            If true, object store has auto increment flag set.
    indexes: list[ObjectStoreIndex]
            Indexes in this object store.
    """

    name: str
    keyPath: KeyPath
    autoIncrement: bool
    indexes: list[ObjectStoreIndex]

    @classmethod
    def from_json(cls, json: dict) -> ObjectStore:
        return cls(
            json["name"],
            KeyPath.from_json(json["keyPath"]),
            json["autoIncrement"],
            [ObjectStoreIndex.from_json(x) for x in json["indexes"]],
        )


@dataclasses.dataclass
class ObjectStoreIndex(Type):
    """Object store index.

    Attributes
    ----------
    name: str
            Index name.
    keyPath: KeyPath
            Index key path.
    unique: bool
            If true, index is unique.
    multiEntry: bool
            If true, index allows multiple entries for a key.
    """

    name: str
    keyPath: KeyPath
    unique: bool
    multiEntry: bool

    @classmethod
    def from_json(cls, json: dict) -> ObjectStoreIndex:
        return cls(
            json["name"],
            KeyPath.from_json(json["keyPath"]),
            json["unique"],
            json["multiEntry"],
        )


@dataclasses.dataclass
class Key(Type):
    """Key.

    Attributes
    ----------
    type: str
            Key type.
    number: Optional[float] = None
            Number value.
    string: Optional[str] = None
            String value.
    date: Optional[float] = None
            Date value.
    array: Optional[list[Key]] = None
            Array value.
    """

    type: str
    number: Optional[float] = None
    string: Optional[str] = None
    date: Optional[float] = None
    array: Optional[list[Key]] = None

    @classmethod
    def from_json(cls, json: dict) -> Key:
        return cls(
            json.get("number"),
            json.get("string"),
            json.get("date"),
            [Key.from_json(x) for x in json["array"]] if "array" in json else None,
        )


@dataclasses.dataclass
class KeyRange(Type):
    """Key range.

    Attributes
    ----------
    lowerOpen: bool
            If true lower bound is open.
    upperOpen: bool
            If true upper bound is open.
    lower: Optional[Key] = None
            Lower bound.
    upper: Optional[Key] = None
            Upper bound.
    """

    lowerOpen: bool
    upperOpen: bool
    lower: Optional[Key] = None
    upper: Optional[Key] = None

    @classmethod
    def from_json(cls, json: dict) -> KeyRange:
        return cls(
            json["lowerOpen"],
            json["upperOpen"],
            Key.from_json(json["lower"]) if "lower" in json else None,
            Key.from_json(json["upper"]) if "upper" in json else None,
        )


@dataclasses.dataclass
class DataEntry(Type):
    """Data entry.

    Attributes
    ----------
    key: runtime.RemoteObject
            Key object.
    primaryKey: runtime.RemoteObject
            Primary key object.
    value: runtime.RemoteObject
            Value object.
    """

    key: runtime.RemoteObject
    primaryKey: runtime.RemoteObject
    value: runtime.RemoteObject

    @classmethod
    def from_json(cls, json: dict) -> DataEntry:
        return cls(
            runtime.RemoteObject.from_json(json["key"]),
            runtime.RemoteObject.from_json(json["primaryKey"]),
            runtime.RemoteObject.from_json(json["value"]),
        )


@dataclasses.dataclass
class KeyPath(Type):
    """Key path.

    Attributes
    ----------
    type: str
            Key path type.
    string: Optional[str] = None
            String value.
    array: Optional[list[str]] = None
            Array value.
    """

    type: str
    string: Optional[str] = None
    array: Optional[list[str]] = None

    @classmethod
    def from_json(cls, json: dict) -> KeyPath:
        return cls(json.get("string"), json.get("array"))


def clear_object_store(securityOrigin: str, databaseName: str, objectStoreName: str):
    """Clears all entries from an object store.

    Parameters
    ----------
    securityOrigin: str
            Security origin.
    databaseName: str
            Database name.
    objectStoreName: str
            Object store name.
    """
    return {
        "method": "IndexedDB.clearObjectStore",
        "params": {
            "securityOrigin": securityOrigin,
            "databaseName": databaseName,
            "objectStoreName": objectStoreName,
        },
    }


def delete_database(securityOrigin: str, databaseName: str):
    """Deletes a database.

    Parameters
    ----------
    securityOrigin: str
            Security origin.
    databaseName: str
            Database name.
    """
    return {
        "method": "IndexedDB.deleteDatabase",
        "params": {"securityOrigin": securityOrigin, "databaseName": databaseName},
    }


def delete_object_store_entries(
    securityOrigin: str, databaseName: str, objectStoreName: str, keyRange: KeyRange
):
    """Delete a range of entries from an object store

    Parameters
    ----------
    securityOrigin: str
    databaseName: str
    objectStoreName: str
    keyRange: KeyRange
            Range of entry keys to delete
    """
    return {
        "method": "IndexedDB.deleteObjectStoreEntries",
        "params": {
            "securityOrigin": securityOrigin,
            "databaseName": databaseName,
            "objectStoreName": objectStoreName,
            "keyRange": keyRange,
        },
    }


def disable():
    """Disables events from backend."""
    return {"method": "IndexedDB.disable", "params": {}}


def enable():
    """Enables events from backend."""
    return {"method": "IndexedDB.enable", "params": {}}


def request_data(
    securityOrigin: str,
    databaseName: str,
    objectStoreName: str,
    indexName: str,
    skipCount: int,
    pageSize: int,
    keyRange: Optional[KeyRange] = None,
):
    """Requests data from object store or index.

    Parameters
    ----------
    securityOrigin: str
            Security origin.
    databaseName: str
            Database name.
    objectStoreName: str
            Object store name.
    indexName: str
            Index name, empty string for object store data requests.
    skipCount: int
            Number of records to skip.
    pageSize: int
            Number of records to fetch.
    keyRange: Optional[KeyRange]
            Key range.

    Returns
    -------
    objectStoreDataEntries: list[DataEntry]
            Array of object store data entries.
    hasMore: bool
            If true, there are more entries to fetch in the given range.
    """
    return filter_unset_parameters(
        {
            "method": "IndexedDB.requestData",
            "params": {
                "securityOrigin": securityOrigin,
                "databaseName": databaseName,
                "objectStoreName": objectStoreName,
                "indexName": indexName,
                "skipCount": skipCount,
                "pageSize": pageSize,
                "keyRange": keyRange,
            },
        }
    )


def get_metadata(securityOrigin: str, databaseName: str, objectStoreName: str):
    """Gets metadata of an object store

    Parameters
    ----------
    securityOrigin: str
            Security origin.
    databaseName: str
            Database name.
    objectStoreName: str
            Object store name.

    Returns
    -------
    entriesCount: float
            the entries count
    keyGeneratorValue: float
            the current value of key generator, to become the next inserted
            key into the object store. Valid if objectStore.autoIncrement
            is true.
    """
    return {
        "method": "IndexedDB.getMetadata",
        "params": {
            "securityOrigin": securityOrigin,
            "databaseName": databaseName,
            "objectStoreName": objectStoreName,
        },
    }


def request_database(securityOrigin: str, databaseName: str):
    """Requests database with given name in given frame.

    Parameters
    ----------
    securityOrigin: str
            Security origin.
    databaseName: str
            Database name.

    Returns
    -------
    databaseWithObjectStores: DatabaseWithObjectStores
            Database with an array of object stores.
    """
    return {
        "method": "IndexedDB.requestDatabase",
        "params": {"securityOrigin": securityOrigin, "databaseName": databaseName},
    }


def request_database_names(securityOrigin: str):
    """Requests database names for given security origin.

    Parameters
    ----------
    securityOrigin: str
            Security origin.

    Returns
    -------
    databaseNames: list[str]
            Database names for origin.
    """
    return {
        "method": "IndexedDB.requestDatabaseNames",
        "params": {"securityOrigin": securityOrigin},
    }
