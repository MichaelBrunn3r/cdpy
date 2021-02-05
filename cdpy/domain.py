import enum


def filter_unset_parameters(method: dict):
    """Remove unset parameters from method dict"""
    method["params"] = {k: v for k, v in method["params"].items() if v != None}
    return method


class Enum(enum.Enum):
    @classmethod
    def from_json(cls, json: str):
        return cls(json)

    def to_json(self):
        return self.value
