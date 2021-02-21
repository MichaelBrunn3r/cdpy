from .cdpy import EventParserError, parse_event
from .protocol import *
from .http_endpoints import (
    Target,
    TargetType,
    activate_page,
    close_page,
    get_protocol,
    get_targets,
    get_version,
    open_new_tab,
)
