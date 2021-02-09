from __future__ import annotations

import dataclasses
from typing import Optional


class DatabaseId(str):
    """Unique identifier of Database object."""

    def __repr__(self):
        return f"DatabaseId({super().__repr__()})"


@dataclasses.dataclass
class Database:
    """Database object.

    Attributes
    ----------
    id: DatabaseId
            Database ID.
    domain: str
            Database domain.
    name: str
            Database name.
    version: str
            Database version.
    """

    id: DatabaseId
    domain: str
    name: str
    version: str

    @classmethod
    def from_json(cls, json: dict) -> Database:
        return cls(
            DatabaseId(json["id"]), json["domain"], json["name"], json["version"]
        )

    def to_json(self) -> dict:
        return {
            "id": str(self.id),
            "domain": self.domain,
            "name": self.name,
            "version": self.version,
        }


@dataclasses.dataclass
class Error:
    """Database error.

    Attributes
    ----------
    message: str
            Error message.
    code: int
            Error code.
    """

    message: str
    code: int

    @classmethod
    def from_json(cls, json: dict) -> Error:
        return cls(json["message"], json["code"])

    def to_json(self) -> dict:
        return {"message": self.message, "code": self.code}


def disable():
    """Disables database tracking, prevents database events from being sent to the client."""
    return {"method": "Database.disable", "params": {}}


def enable():
    """Enables database tracking, database events will now be delivered to the client."""
    return {"method": "Database.enable", "params": {}}


def execute_sql(databaseId: DatabaseId, query: str):
    """
    Parameters
    ----------
    databaseId: DatabaseId
    query: str

    Returns
    -------
    columnNames: Optional[list[str]]
    values: Optional[list[any]]
    sqlError: Optional[Error]
    """
    return {
        "method": "Database.executeSQL",
        "params": {"databaseId": databaseId, "query": query},
    }


def get_database_table_names(databaseId: DatabaseId):
    """
    Parameters
    ----------
    databaseId: DatabaseId

    Returns
    -------
    tableNames: list[str]
    """
    return {
        "method": "Database.getDatabaseTableNames",
        "params": {"databaseId": databaseId},
    }
