from __future__ import annotations

import dataclasses
import enum
from typing import Optional

from .common import Type, filter_unset_parameters


def disable():
    """Disables inspector domain notifications."""
    return {"method": "Inspector.disable", "params": {}}


def enable():
    """Enables inspector domain notifications."""
    return {"method": "Inspector.enable", "params": {}}
