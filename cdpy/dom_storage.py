from __future__ import annotations

import dataclasses
from typing import Generator


@dataclasses.dataclass
class StorageId:
    """DOM Storage identifier.

    Attributes
    ----------
    securityOrigin: str
            Security origin for the storage.
    isLocalStorage: bool
            Whether the storage is local storage (not session storage).
    """

    securityOrigin: str
    isLocalStorage: bool

    @classmethod
    def from_json(cls, json: dict) -> StorageId:
        return cls(json["securityOrigin"], json["isLocalStorage"])

    def to_json(self) -> dict:
        return {
            "securityOrigin": self.securityOrigin,
            "isLocalStorage": self.isLocalStorage,
        }


class Item(list[str]):
    """DOM Storage item."""

    def __repr__(self):
        return f"Item({super().__repr__()})"


def clear(storageId: StorageId) -> dict:
    """
    Parameters
    ----------
    storageId: StorageId
    """
    return {"method": "DOMStorage.clear", "params": {"storageId": storageId.to_json()}}


def disable() -> dict:
    """Disables storage tracking, prevents storage events from being sent to the client."""
    return {"method": "DOMStorage.disable", "params": {}}


def enable() -> dict:
    """Enables storage tracking, storage events will now be delivered to the client."""
    return {"method": "DOMStorage.enable", "params": {}}


def get_dom_storage_items(storageId: StorageId) -> Generator[dict, dict, list[Item]]:
    """
    Parameters
    ----------
    storageId: StorageId

    Returns
    -------
    entries: list[Item]
    """
    response = yield {
        "method": "DOMStorage.getDOMStorageItems",
        "params": {"storageId": storageId.to_json()},
    }
    return [Item(e) for e in response]


def remove_dom_storage_item(storageId: StorageId, key: str) -> dict:
    """
    Parameters
    ----------
    storageId: StorageId
    key: str
    """
    return {
        "method": "DOMStorage.removeDOMStorageItem",
        "params": {"storageId": storageId.to_json(), "key": key},
    }


def set_dom_storage_item(storageId: StorageId, key: str, value: str) -> dict:
    """
    Parameters
    ----------
    storageId: StorageId
    key: str
    value: str
    """
    return {
        "method": "DOMStorage.setDOMStorageItem",
        "params": {"storageId": storageId.to_json(), "key": key, "value": value},
    }


@dataclasses.dataclass
class DomStorageItemAdded:
    """
    Attributes
    ----------
    storageId: StorageId
    key: str
    newValue: str
    """

    storageId: StorageId
    key: str
    newValue: str

    @classmethod
    def from_json(cls, json: dict) -> DomStorageItemAdded:
        return cls(
            StorageId.from_json(json["storageId"]), json["key"], json["newValue"]
        )


@dataclasses.dataclass
class DomStorageItemRemoved:
    """
    Attributes
    ----------
    storageId: StorageId
    key: str
    """

    storageId: StorageId
    key: str

    @classmethod
    def from_json(cls, json: dict) -> DomStorageItemRemoved:
        return cls(StorageId.from_json(json["storageId"]), json["key"])


@dataclasses.dataclass
class DomStorageItemUpdated:
    """
    Attributes
    ----------
    storageId: StorageId
    key: str
    oldValue: str
    newValue: str
    """

    storageId: StorageId
    key: str
    oldValue: str
    newValue: str

    @classmethod
    def from_json(cls, json: dict) -> DomStorageItemUpdated:
        return cls(
            StorageId.from_json(json["storageId"]),
            json["key"],
            json["oldValue"],
            json["newValue"],
        )


@dataclasses.dataclass
class DomStorageItemsCleared:
    """
    Attributes
    ----------
    storageId: StorageId
    """

    storageId: StorageId

    @classmethod
    def from_json(cls, json: dict) -> DomStorageItemsCleared:
        return cls(StorageId.from_json(json["storageId"]))
