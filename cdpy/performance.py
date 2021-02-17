from __future__ import annotations

import dataclasses
from typing import Generator, Optional

from deprecated.sphinx import deprecated

from .common import filter_none


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


def disable() -> dict:
    """Disable collecting and reporting metrics."""
    return {"method": "Performance.disable", "params": {}}


def enable(timeDomain: Optional[str] = None) -> dict:
    """Enable collecting and reporting metrics.

    Parameters
    ----------
    timeDomain: Optional[str]
            Time domain to use for collecting and reporting duration metrics.
    """
    return {
        "method": "Performance.enable",
        "params": filter_none({"timeDomain": timeDomain}),
    }


@deprecated(version=1.3)
def set_time_domain(timeDomain: str) -> dict:
    """Sets time domain to use for collecting and reporting duration metrics.
    Note that this must be called before enabling metrics collection. Calling
    this method while metrics collection is enabled returns an error.

    Parameters
    ----------
    timeDomain: str
            Time domain

    **Experimental**
    """
    return {"method": "Performance.setTimeDomain", "params": {"timeDomain": timeDomain}}


def get_metrics() -> Generator[dict, dict, list[Metric]]:
    """Retrieve current values of run-time metrics.

    Returns
    -------
    metrics: list[Metric]
            Current values for run-time metrics.
    """
    response = yield {"method": "Performance.getMetrics", "params": {}}
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
