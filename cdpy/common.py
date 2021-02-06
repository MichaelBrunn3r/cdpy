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

            # Extract type inside Optional
            if is_optional:
                # Field type is of type typing.Optional[...].
                field_type = data.type.__args__[0]

            # Skip fields with value 'None'
            if value == None:
                args[field] = value
            else:
                args[field] = field_type(value)

        return cls(**args)
