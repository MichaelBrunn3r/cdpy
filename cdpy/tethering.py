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
