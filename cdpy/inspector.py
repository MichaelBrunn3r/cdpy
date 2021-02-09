from __future__ import annotations

import dataclasses


def disable():
    """Disables inspector domain notifications."""
    return {"method": "Inspector.disable", "params": {}}


def enable():
    """Enables inspector domain notifications."""
    return {"method": "Inspector.enable", "params": {}}
