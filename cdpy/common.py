import typing
from dataclasses import _MISSING_TYPE

from . import dom


def filter_unset_parameters(method: dict):
    """Remove unset parameters from method dict"""
    method["params"] = {k: v for k, v in method["params"].items() if v != None}
    return method


class Type:
    @classmethod
    def from_json(cls, json: dict):
        args = {}

        for field, data in cls.__dataclass_fields__.items():
            field_type = data.type
            is_optional = data.default == None

            # Check if the field in the json
            if field not in json:
                if is_optional:
                    continue
                else:
                    raise Exception("Missing required argument '{}'".format(field))

            value = json[field]

            # Extract type from
            if is_optional:
                field_type = data.type.__args__[0]

            # Skip fields with value 'None'
            if value == None:
                args[field] = value
                continue

            # Is field_type from typing module? (e.g. List, Set, Optional, ...)
            if type(field_type) == typing._GenericAlias:
                origin = field_type.__origin__

                # List, Set, ...
                if type(origin) == type:
                    args[field] = origin(value)
                    continue
            else:
                args[field] = field_type(value)

        return cls(**args)
