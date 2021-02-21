from __future__ import annotations

import dataclasses
from typing import Any, Generator, Optional


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

    def to_json(self):
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

    def to_json(self):
        return {"message": self.message, "code": self.code}


def disable() -> dict:
    """Disables database tracking, prevents database events from being sent to the client."""
    return {"method": "Database.disable", "params": {}}


def enable() -> dict:
    """Enables database tracking, database events will now be delivered to the client."""
    return {"method": "Database.enable", "params": {}}


def execute_sql(databaseId: DatabaseId, query: str) -> Generator[dict, dict, dict]:
    """
    Parameters
    ----------
    databaseId: DatabaseId
    query: str

    Returns
    -------
    columnNames: Optional[list[str]]
    values: Optional[list[Any]]
    sqlError: Optional[Error]
    """
    response = yield {
        "method": "Database.executeSQL",
        "params": {"databaseId": str(databaseId), "query": query},
    }
    return {
        "columnNames": response.get("columnNames"),
        "values": response.get("values"),
        "sqlError": Error.from_json(response["sqlError"])
        if "sqlError" in response
        else None,
    }


def get_database_table_names(
    databaseId: DatabaseId,
) -> Generator[dict, dict, list[str]]:
    """
    Parameters
    ----------
    databaseId: DatabaseId

    Returns
    -------
    tableNames: list[str]
    """
    response = yield {
        "method": "Database.getDatabaseTableNames",
        "params": {"databaseId": str(databaseId)},
    }
    return response["tableNames"]


@dataclasses.dataclass
class AddDatabase:
    """
    Attributes
    ----------
    database: Database
    """

    database: Database

    @classmethod
    def from_json(cls, json: dict) -> AddDatabase:
        return cls(Database.from_json(json["database"]))
