import enum
from dataclasses import dataclass
from typing import Optional

from .protocol._event_parsers import event_parsers


class TargetType(enum.Enum):
    """reference: https://source.chromium.org/chromium/chromium/src/+/master:content/browser/devtools/devtools_agent_host_impl.cc"""

    PAGE = "page"
    IFRAME = "iframe"
    WORKER = "worker"
    SHARED_WORKER = "shared_worker"
    SERVICE_WORKER = "service_worker"
    BROWSER = "browser"
    WEBVIEW = "webview"
    OTHER = "other"


@dataclass
class Target:
    description: str
    devtools_frontend_url: str
    id: str
    title: str
    type: TargetType
    url: str
    websocket_debugg_url: str
    parentId: Optional[str]

    @classmethod
    def from_json(cls, json):
        return cls(
            json["description"],
            json["devtoolsFrontendUrl"],
            json["id"],
            json["title"],
            TargetType(json["type"]),
            json["url"],
            json["webSocketDebuggerUrl"],
            json.get("parentId"),
        )


class EventParserError(Exception):
    pass


def parse_event(event_json: dict):
    if not event_json or not "method" in event_json:
        raise EventParserError("Can't parse event, missing item: 'method'")

    if not "params" in event_json:
        raise EventParserError("Can't parse event, missing item: 'params'")

    event_name = event_json["method"]
    parser = event_parsers.get(event_name)

    if not parser:
        raise EventParserError(f"Couldn't find parser for event: {event_name}")

    return parser.from_json(event_json["params"])
