from __future__ import annotations

import dataclasses


def clear_device_orientation_override() -> dict:
    """Clears the overridden Device Orientation."""
    return {"method": "DeviceOrientation.clearDeviceOrientationOverride", "params": {}}


def set_device_orientation_override(alpha: float, beta: float, gamma: float) -> dict:
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
