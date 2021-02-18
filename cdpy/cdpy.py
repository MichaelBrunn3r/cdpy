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
