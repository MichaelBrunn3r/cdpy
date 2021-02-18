import enum
from dataclasses import dataclass
from typing import Callable, Iterable, Iterator, Optional

from ._event_parsers import event_parsers


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


# from https://source.chromium.org/chromium/chromium/src/+/master:content/browser/devtools/devtools_agent_host_impl.cc
class TargetType(enum.Enum):
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


def get_targets(
    remote_debugging_url: str,
    get_target_json: Callable[[str], Iterable],
    filter_types: Optional[list[TargetType]] = None,
) -> Iterator[Target]:
    """
    Parameters
    ----------
    remote_debugging_url: str
        Url to the chrome devtools remote-debugging-port of a running browser instance
    get_target_json:
        Callable that takes an url, requests it and returns the json value of the response
    filter_types: Optional[list[TargetType]]
        Only return targets of these types
    """

    targets_json = get_target_json(f"{remote_debugging_url}/json/list")
    targets = map(lambda t: Target.from_json(t), targets_json)

    if filter_types != None and len(filter_types) > 0:
        targets = filter(lambda t: t.type in filter_types, targets)

    return targets
