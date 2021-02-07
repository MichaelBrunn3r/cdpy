import typing
from typing import ForwardRef, Optional


def filter_unset_parameters(method: dict):
    """Remove unset parameters from method dict"""
    method["params"] = {k: v for k, v in method["params"].items() if v != None}
    return method


class Type:
    @classmethod
    def from_json(cls, json: dict):
        init_args = {}

        dataclass_fields = cls.__dataclass_fields__
        field_types = typing.get_type_hints(cls)
        for arg, value in json.items():
            # Ignore args that don't map to a class field
            if not arg in dataclass_fields:
                continue

            field = dataclass_fields[arg]
            field_type = field_types[arg]
            is_optional = field.default == None

            # Extract type inside Optional
            if is_optional:
                # Field type is of form typing.Optional[...].
                field_type = field_type.__args__[0]

            if value == None:
                init_args[arg] = value
            elif issubclass(field_type, Type):
                init_args[arg] = field_type.from_json(value)
            elif hasattr(field_type, "__origin__") and field_type.__origin__ == list:
                items_type = field_type.__args__[0]
                print(items_type, type(items_type))
                if type(items_type) == str:
                    items_type = eval(items_type)

                if issubclass(items_type, Type):
                    items = map(lambda item: items_type.from_json(item), value)
                else:
                    items = map(lambda item: items_type(item), value)
                init_args[arg] = list(items)
            else:
                init_args[arg] = field_type(value)

        return cls(**init_args)
