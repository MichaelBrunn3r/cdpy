from __future__ import annotations

import dataclasses


def disable() -> dict:
    """Disables inspector domain notifications."""
    return {"method": "Inspector.disable", "params": {}}


def enable() -> dict:
    """Enables inspector domain notifications."""
    return {"method": "Inspector.enable", "params": {}}
