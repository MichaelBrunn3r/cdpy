from __future__ import annotations

import dataclasses
import enum
from typing import Optional

from .common import Type, filter_unset_parameters


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
