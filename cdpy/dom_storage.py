from __future__ import annotations

import dataclasses


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


def clear(storageId: StorageId):
    """
    Parameters
    ----------
    storageId: StorageId
    """
    return {"method": "DOMStorage.clear", "params": {"storageId": storageId}}


def disable():
    """Disables storage tracking, prevents storage events from being sent to the client."""
    return {"method": "DOMStorage.disable", "params": {}}


def enable():
    """Enables storage tracking, storage events will now be delivered to the client."""
    return {"method": "DOMStorage.enable", "params": {}}


def get_dom_storage_items(storageId: StorageId):
    """
    Parameters
    ----------
    storageId: StorageId

    Returns
    -------
    entries: list[Item]
    """
    return {
        "method": "DOMStorage.getDOMStorageItems",
        "params": {"storageId": storageId},
    }


def remove_dom_storage_item(storageId: StorageId, key: str):
    """
    Parameters
    ----------
    storageId: StorageId
    key: str
    """
    return {
        "method": "DOMStorage.removeDOMStorageItem",
        "params": {"storageId": storageId, "key": key},
    }


def set_dom_storage_item(storageId: StorageId, key: str, value: str):
    """
    Parameters
    ----------
    storageId: StorageId
    key: str
    value: str
    """
    return {
        "method": "DOMStorage.setDOMStorageItem",
        "params": {"storageId": storageId, "key": key, "value": value},
    }
