from __future__ import annotations

import dataclasses


@dataclasses.dataclass
class Domain:
    """Description of the protocol domain.

    Attributes
    ----------
    name: str
            Domain name.
    version: str
            Domain version.
    """

    name: str
    version: str

    @classmethod
    def from_json(cls, json: dict) -> Domain:
        return cls(json["name"], json["version"])

    def to_json(self) -> dict:
        return {"name": self.name, "version": self.version}


def get_domains():
    """Returns supported domains.

    Returns
    -------
    domains: list[Domain]
            List of supported domains.
    """
    return {"method": "Schema.getDomains", "params": {}}
