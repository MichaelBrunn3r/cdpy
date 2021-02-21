def filter_none(json: dict):
    return {k: v for k, v in json.items() if v != None}
