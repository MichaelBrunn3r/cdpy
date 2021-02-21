from __future__ import annotations

import dataclasses
from typing import Generator


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

    def to_json(self):
        return {"name": self.name, "version": self.version}


def get_domains() -> Generator[dict, dict, list[Domain]]:
    """Returns supported domains.

    Returns
    -------
    domains: list[Domain]
            List of supported domains.
    """
    response = yield {"method": "Schema.getDomains", "params": {}}
    return [Domain.from_json(d) for d in response["domains"]]
