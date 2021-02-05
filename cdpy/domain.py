def filter_unset_parameters(method: dict):
    """Remove unset parameters from method dict"""
    method["params"] = {k: v for k, v in method["params"].items() if v != None}
    return method
