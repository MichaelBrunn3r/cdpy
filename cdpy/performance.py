from __future__ import annotations

import dataclasses
from typing import Optional

from .common import filter_unset_parameters


@dataclasses.dataclass
class Metric:
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

    def to_json(self) -> dict:
        return {"name": self.name, "value": self.value}


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


def parse_get_metrics_response(response):
    return [Metric.from_json(m) for m in response["metrics"]]


@dataclasses.dataclass
class Metrics:
    """Current values of the metrics.

    Attributes
    ----------
    metrics: list[Metric]
            Current values of the metrics.
    title: str
            Timestamp title.
    """

    metrics: list[Metric]
    title: str

    @classmethod
    def from_json(cls, json: dict) -> Metrics:
        return cls([Metric.from_json(m) for m in json["metrics"]], json["title"])
