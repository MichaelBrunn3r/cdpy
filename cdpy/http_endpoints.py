from typing import Callable, Iterable, Iterator, Optional
from .cdpy import Target, TargetType


def get_targets(
    remote_debugging_url: str,
    request_json: Callable[[str], Iterable],
    filter_types: Optional[list[TargetType]] = None,
) -> Iterator[Target]:
    """
    Parameters
    ----------
    remote_debugging_url: str
        Url to the chrome devtools remote-debugging-port of a running browser instance
    request_json:
        Callable that takes an url, requests it and returns the json value of the response
    filter_types: Optional[list[TargetType]]
        Only return targets of these types
    """

    targets_json = request_json(f"{remote_debugging_url}/json/list")
    targets = map(lambda t: Target.from_json(t), targets_json)

    if filter_types != None and len(filter_types) > 0:
        targets = filter(lambda t: t.type in filter_types, targets)

    return targets


def get_version(remote_debugging_url: str, request_json: Callable[[str], dict]):
    """ Browser version metadata """
    return request_json(f"{remote_debugging_url}/json/version")


def open_new_tab(
    remote_debugging_url: str, request_json: Callable[[str], dict], tab_url: str = ""
):
    """Opens a new tab and responds with its websocket target

    Parameters
    ----------
    remote_debugging_url: str
        Url to the chrome devtools remote-debugging-port of a running browser instance
    request_json:
        Callable that takes an url, requests it and returns the json value of the response
    tab_url: str
        The url the tab should be opened on
    """

    tab_json = request_json(f"{remote_debugging_url}/json/new?{tab_url}")
    return Target.from_json(tab_json)


def activate_page(
    remote_debugging_url: str, request: Callable[[str], Iterable], target_id: str
):
    """Brings a page into the foreground (activate a tab).

    Parameters
    ----------
    remote_debugging_url: str
        Url to the chrome devtools remote-debugging-port of a running browser instance
    request:
        Callable that takes an url and requests it
    target_id: str
        The target id of the page to activate

    Responses
    ---------
    200:
        Target activated
    404:
        No such target id
    """
    return request(f"{remote_debugging_url}/json/activate/{target_id}")


def close_page(
    remote_debugging_url: str, request: Callable[[str], Iterable], target_id: str
):
    """Closes the target page identified by targetId.

    Parameters
    ----------
    remote_debugging_url: str
        Url to the chrome devtools remote-debugging-port of a running browser instance
    request:
        Callable that takes an url and requests it
    target_id: str
        The target id of the page to close

    Responses
    ---------
    200:
        Target is closing
    404:
        No such target id
    """
    return request(f"{remote_debugging_url}/json/close/{target_id}")


def get_protocol(remote_debugging_url: str, request_json: Callable[[str], Iterable]):
    """ The current devtools protocol, as JSON """
    return request_json(f"{remote_debugging_url}/json/protocol")
