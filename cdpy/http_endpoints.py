import enum
from dataclasses import dataclass
from typing import Callable, Iterable, Iterator, Optional


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
