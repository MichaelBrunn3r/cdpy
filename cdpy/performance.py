from __future__ import annotations

import dataclasses
import enum
from typing import Optional

from .common import Type, filter_unset_parameters


@dataclasses.dataclass
class Metric(Type):
    """Run-time execution metric.

    Attributes
    ----------
    name: str
            Metric name.
    value: float
            Metric value.
    """

    name: str
    value: float

    @classmethod
    def from_json(cls, json: dict) -> Metric:
        return cls(json["name"], json["value"])


def disable():
    """Disable collecting and reporting metrics."""
    return {"method": "Performance.disable", "params": {}}


def enable(timeDomain: Optional[str] = None):
    """Enable collecting and reporting metrics.

    Parameters
    ----------
    timeDomain: Optional[str]
            Time domain to use for collecting and reporting duration metrics.
    """
    return filter_unset_parameters(
        {"method": "Performance.enable", "params": {"timeDomain": timeDomain}}
    )


def set_time_domain(timeDomain: str):
    """Sets time domain to use for collecting and reporting duration metrics.
    Note that this must be called before enabling metrics collection. Calling
    this method while metrics collection is enabled returns an error.

    **Experimental**

    **Deprectated**

    Parameters
    ----------
    timeDomain: str
            Time domain
    """
    return {"method": "Performance.setTimeDomain", "params": {"timeDomain": timeDomain}}


def get_metrics():
    """Retrieve current values of run-time metrics.

    Returns
    -------
    metrics: list[Metric]
            Current values for run-time metrics.
    """
    return {"method": "Performance.getMetrics", "params": {}}
