from __future__ import annotations

import dataclasses
import enum
from typing import Optional

from .common import Type, filter_unset_parameters


def clear_device_orientation_override():
    """Clears the overridden Device Orientation."""
    return {"method": "DeviceOrientation.clearDeviceOrientationOverride", "params": {}}


def set_device_orientation_override(alpha: float, beta: float, gamma: float):
    """Overrides the Device Orientation.

    Parameters
    ----------
    alpha: float
            Mock alpha
    beta: float
            Mock beta
    gamma: float
            Mock gamma
    """
    return {
        "method": "DeviceOrientation.setDeviceOrientationOverride",
        "params": {"alpha": alpha, "beta": beta, "gamma": gamma},
    }
