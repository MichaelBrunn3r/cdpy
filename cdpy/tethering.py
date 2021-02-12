from __future__ import annotations

import dataclasses


def bind(port: int):
    """Request browser port binding.

    Parameters
    ----------
    port: int
            Port number to bind.
    """
    return {"method": "Tethering.bind", "params": {"port": port}}


def unbind(port: int):
    """Request browser port unbinding.

    Parameters
    ----------
    port: int
            Port number to unbind.
    """
    return {"method": "Tethering.unbind", "params": {"port": port}}


@dataclasses.dataclass
class Accepted:
    """Informs that port was successfully bound and got a specified connection id.

    Attributes
    ----------
    port: int
            Port number that was successfully bound.
    connectionId: str
            Connection id to be used.
    """

    port: int
    connectionId: str

    @classmethod
    def from_json(cls, json: dict) -> Accepted:
        return cls(json["port"], json["connectionId"])
