from __future__ import annotations

import ast
import enum
import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import inflection
import requests
import typer

from generator.ast_utils import *

GENERATE_DIR = script_dir = Path(os.path.abspath(os.path.split(__file__)[0]))
BROWSER_PROTOCOL_FILENAME_TEMPLATE = "browser_protocol-v{}.{}.json"
JS_PROTOCOL_FILENAME_TEMPLATE = "js_protocol-v{}.{}.json"

JS_TYPE_TO_BUILTIN_MAP = {
    "string": "str",
    "integer": "int",
    "number": "float",
    "boolean": "bool",
    "array": "list",
    "object": "dict",
}

app = typer.Typer()

# Init logger
log_level = getattr(logging, os.environ.get("LOG_LEVEL", "info").upper())
logging.basicConfig(level=log_level)
logger = logging.getLogger(__name__)


class GlobalContext:
    def __init__(self):
        self.domains: dict[str, CDPDomain] = {}

    def get_type_by_ref(self, reference: str) -> CDPType | None:
        domain_name, type_name = get_reference_parts(reference)
        domain = self.domains[domain_name]
        for type_ in domain.types:
            if type_.id == type_name:
                return type_


class ModuleContext:
    def __init__(
        self, module_name: str, domain_name: str, global_context: GlobalContext
    ):
        self.global_context = global_context
        self.domain_name = domain_name
        self.module_name = module_name
        self.required_imports: dict[str, set] = {}

    def require(self, package: str, name: Optional[str]):
        if name and package in self.required_imports:
            self.required_imports[package].add(name)
        else:
            names = set()
            if name:
                names.add(name)
            self.required_imports[package] = names

    def get_type_by_ref(self, reference: str) -> CDPType | None:
        domain_name, type_name = get_reference_parts(reference)
        if not domain_name:
            domain_name = self.domain_name

        return self.global_context.get_type_by_ref(domain_name + "." + type_name)


def domain_to_module_name(domain: str):
    return snake_case(domain)


def snake_case(string: str):
    return inflection.underscore(string)


def create_type_annotation(
    type, ref, items: CDPItems, optional, context: ModuleContext
):
    if items:
        annot = f"list[{create_type_annotation(items.type, items.ref, None, False, context)}]"
    elif type:
        annot = JS_TYPE_TO_BUILTIN_MAP.get(type, type)
    else:
        referenced_domain, referenced_type = get_reference_parts(ref)

        if not referenced_domain or referenced_domain == context.domain_name:
            # References type in current domain -> module can be omitted
            annot = referenced_type
        else:
            referenced_module = domain_to_module_name(referenced_domain)
            context.require(".", referenced_module)
            annot = f"{referenced_module}.{referenced_type}"

    if optional:
        annot = f"Optional[{annot}]"

    return annot


def get_reference_parts(reference: str) -> tuple[Optional[str], str]:
    """Splits a reference into a domain and a name part"""
    parts = reference.split(".")
    return tuple(parts) if len(parts) > 1 else (None, parts[0])


@dataclass
class CDPItems:
    type: Optional[str]
    ref: Optional[str]
    context: ModuleContext

    @classmethod
    def from_json(cls, item: dict, context: ModuleContext):
        return cls(item.get("type"), item.get("$ref"), context)

    def create_type_annotation(self):
        return create_type_annotation(self.type, self.type, None, False, self.context)


class CDPPropertyCategory(enum.Enum):
    BUILTIN = 0
    BUILTIN_LIST = 1
    TYPELESS_ENUM = 2
    SIMPLE = 3
    SIMPLE_LIST = 4
    ENUM = 5
    ENUM_LIST = 6
    OBJECT = 7
    OBJECT_LIST = 8

    @property
    def does_not_require_parsing(self):
        return self in (self.BUILTIN, self.BUILTIN_LIST, self.TYPELESS_ENUM)

    @property
    def does_not_require_unparsing(self):
        return self.does_not_require_parsing

    @property
    def parse_with_from_json(self):
        """Wether the types of this category should be parsed with a from_json call (e.g. SomeType.from_json(json))"""
        return self in (self.OBJECT, self.OBJECT_LIST)

    @property
    def unparse_with_to_json(self):
        return self.parse_with_from_json

    @property
    def parse_with_constructor(self):
        """Wether the types of this category should be parsed with a constructor (e.g. SomeType(json), [SomeType(j) for j in json])"""
        return self in (
            self.SIMPLE,
            self.ENUM,
            self.SIMPLE_LIST,
            self.ENUM_LIST,
        )

    @property
    def unparse_with_base_type(self):
        return self.parse_with_constructor

    def from_cdp_type(type: CDPType, is_list: bool):
        """Returns a category according to a properties type"""
        if is_list:
            return {
                CDPTypeCategory.BUILTIN: CDPPropertyCategory.SIMPLE_LIST,
                CDPTypeCategory.BUILTIN_LIST: CDPPropertyCategory.SIMPLE_LIST,
                CDPTypeCategory.ENUM: CDPPropertyCategory.ENUM_LIST,
                CDPTypeCategory.OBJECT: CDPPropertyCategory.OBJECT_LIST,
                CDPTypeCategory.OBJECT_LIST: CDPPropertyCategory.OBJECT_LIST,
            }.get(type.category)
        else:
            return {
                CDPTypeCategory.BUILTIN: CDPPropertyCategory.SIMPLE,
                CDPTypeCategory.BUILTIN_LIST: CDPPropertyCategory.SIMPLE,
                CDPTypeCategory.ENUM: CDPPropertyCategory.ENUM,
                CDPTypeCategory.OBJECT: CDPPropertyCategory.OBJECT,
            }.get(type.category)


@dataclass
class CDPProperty:
    name: str
    description: Optional[str]
    type: Optional[str]
    ref: Optional[str]
    enum_values: Optional[list[str]]
    items: Optional[CDPItems]
    optional: bool
    experimental: bool
    deprecated: bool
    context: ModuleContext

    @property
    def category(self):
        if not hasattr(self, "_category"):
            if self.items:
                # Property is a list
                if self.items.type:
                    # Property is a list of primitves/builtins
                    self._category = CDPPropertyCategory.BUILTIN_LIST
                else:
                    # Property is a list of cdp types
                    items_type = self.context.get_type_by_ref(self.items.ref)
                    self._category = CDPPropertyCategory.from_cdp_type(items_type, True)
            elif self.enum_values:
                self._category = CDPPropertyCategory.TYPELESS_ENUM
            elif self.ref:
                ref_type = self.context.get_type_by_ref(self.ref)
                self._category = CDPPropertyCategory.from_cdp_type(ref_type, False)
            elif self.type:
                self._category = CDPPropertyCategory.BUILTIN
            else:
                raise Exception("Can't determin cdp property type")

        return self._category

    @property
    def is_list_of_references(self):
        """Checks if the property is a list and its items are references to an type"""
        return self.category in [
            CDPPropertyCategory.SIMPLE_LIST,
            CDPPropertyCategory.ENUM_LIST,
            CDPPropertyCategory.OBJECT_LIST,
        ]

    @classmethod
    def from_json(cls, property: dict, context: ModuleContext) -> CDPProperty:
        items = property.get("items")
        optional = property.get("optional", False)
        if optional:
            context.require("typing", "Optional")

        return cls(
            property["name"],
            property.get("description"),
            property.get("type"),
            property.get("$ref"),
            property.get("enum"),
            CDPItems.from_json(items, context) if items else None,
            optional,
            property.get("experimental", False),
            property.get("deprecated", False),
            context,
        )

    def to_ast(self):
        annotation = create_type_annotation(
            self.type, self.ref, self.items, self.optional, self.context
        )
        return ast.arg(self.name, ast.Name(annotation))

    def to_docstring(self):
        annotation = create_type_annotation(
            self.type, self.ref, self.items, self.optional, self.context
        )
        lines = [f"{self.name}: {annotation}"]

        if self.description and not self.description.isspace():
            lines += map(lambda l: "\t" + l, self.description.split("\n"))
        return lines


@dataclass
class CDPParameter(CDPProperty):
    pass


@dataclass
class CDPReturn(CDPProperty):
    pass


@dataclass
class CDPAttribute(CDPProperty):
    def to_ast(self):
        annotation = create_type_annotation(
            self.type, self.ref, self.items, self.optional, self.context
        )
        value = (
            ast.Constant(None) if self.optional else None
        )  # Default value if optional
        return ast.AnnAssign(
            ast.Name(self.name), ast.Name(annotation), value=value, simple=1
        )


class CDPTypeCategory(enum.Enum):
    BUILTIN = 0
    BUILTIN_LIST = 1
    ENUM = 2
    OBJECT = 3
    OBJECT_LIST = 4


@dataclass
class CDPType:
    id: str
    description: Optional[str]
    type: str
    items: CDPItems
    enum_values: Optional[list[str]]
    attributes: Optional[list[CDPAttribute]]
    context: ModuleContext
    has_optional_attributes: bool

    @property
    def category(self) -> CDPTypeCategory:
        if not hasattr(self, "_category"):
            if self.items:
                if self.items.type:
                    self._category = CDPTypeCategory.BUILTIN_LIST
                else:
                    self._category = CDPTypeCategory.OBJECT_LIST
            elif self.enum_values:
                self._category = CDPTypeCategory.ENUM
            elif self.attributes:
                self._category = CDPTypeCategory.OBJECT
            else:
                self._category = CDPTypeCategory.BUILTIN

        return self._category

    def create_reference(self, from_context: ModuleContext):
        """Create a reference to this type from a context"""
        if self.context != from_context:
            return f"{self.context.module_name}.{self.id}"
        else:
            return self.id

    @classmethod
    def from_json(cls, json: dict, context: ModuleContext):
        has_optional_attributes = False
        items = json.get("items")

        attributes = json.get("properties")
        if attributes:
            for i, attr_json in enumerate(attributes):
                attr = CDPAttribute.from_json(attr_json, context)
                attributes[i] = attr

                if attr.optional:
                    has_optional_attributes = True

            attributes.sort(
                key=lambda p: p.optional
            )  # Default value attributes after non-default attributes

        return cls(
            json["id"],
            json.get("description"),
            json["type"],
            CDPItems.from_json(items, context) if items else None,
            json.get("enum"),
            attributes,
            context,
            has_optional_attributes,
        )

    def to_ast(self):
        if self.category in [CDPTypeCategory.BUILTIN, CDPTypeCategory.BUILTIN_LIST]:
            return self.create_builtin_ast()
        elif self.category == CDPTypeCategory.ENUM:
            self.context.require("enum", None)
            return self.create_enum_ast()
        elif self.category == CDPTypeCategory.OBJECT:
            return self.create_object_ast()
        elif self.category == CDPTypeCategory.OBJECT_LIST:
            return self.create_object_list_ast()
        else:
            raise Exception(
                f"Can't generate AST for type '{self.context.domain_name}.{self.id}'"
            )

    def create_builtin_ast(self):
        """Create the AST for a simple type or simple list type"""
        base = create_type_annotation(self.type, None, self.items, False, self.context)

        return ast_classdef(
            self.id,
            [self.create_docstring(), self.create_builtin_repr_function()],
            [base],
        )

    def create_builtin_repr_function(self):
        """Create the __repr__ function for a simple type"""
        return ast_function(
            "__repr__",
            ast_args([ast.arg("self", None)]),
            [ast_from_str(f"return f'{self.id}({{super().__repr__()}})'")],
        )

    def create_enum_ast(self):
        """Create the AST for an enum type"""
        body = [self.create_docstring()]

        # Add enum values
        for v in self.enum_values:
            body.append(
                ast.Assign([ast.Name(snake_case(v).upper())], ast.Str(v), lineno=0)
            )

        return ast_classdef(self.id, body, ["enum.Enum"])

    def create_object_ast(self):
        body = [self.create_docstring()]

        for attr in self.attributes:
            body.append(attr.to_ast())

        body.append(self.create_object_from_json_function())
        body.append(self.create_object_to_json_function())

        return ast_classdef(self.id, body, decorators=["dataclasses.dataclass"])

    def create_object_from_json_function(self):
        cls_args = []
        for attr in self.attributes:
            category = attr.category
            attr_json_value = ast.Subscript(ast.Name("json"), ast.Constant(attr.name))

            if category.does_not_require_parsing:
                if attr.optional:
                    arg = ast_call(
                        ast.Attribute(ast.Name("json"), "get"),
                        [ast.Constant(attr.name)],
                    )
                else:
                    arg = attr_json_value
            elif attr.is_list_of_references:
                items_type_name = self.context.get_type_by_ref(
                    attr.items.ref
                ).create_reference(self.context)

                if category.parse_with_constructor:
                    arg = ast_list_comp(
                        ast_call(items_type_name, [ast.Name("x")]), "x", attr_json_value
                    )
                elif category.parse_with_from_json:
                    from_json_call = ast_call(
                        ast.Attribute(ast.Name(items_type_name), "from_json"), ["x"]
                    )
                    arg = ast_list_comp(from_json_call, "x", attr_json_value)
                else:
                    raise Exception(
                        f"Can't parse argument: {self.context.domain_name}.{self.id}.{attr.name}"
                    )
            else:
                referenced_type_name = self.context.get_type_by_ref(
                    attr.ref
                ).create_reference(self.context)

                if category.parse_with_constructor:
                    arg = ast_call(referenced_type_name, [attr_json_value])
                elif category.parse_with_from_json:
                    arg = ast_call(
                        ast.Attribute(ast.Name(referenced_type_name), "from_json"),
                        [attr_json_value],
                    )
                else:
                    raise Exception(
                        f"Can't parse argument: {self.context.domain_name}.{self.id}.{attr.name}"
                    )

            # Wrap argument in 'if ... else None' if the attribute is optional.
            # Primitives are calling 'dict.get()' instead.
            if attr.optional and not category.does_not_require_parsing:
                is_in_json_condition = ast.Compare(
                    ast.Constant(attr.name), [ast.In()], [ast.Name("json")]
                )
                arg = ast.IfExp(is_in_json_condition, arg, ast.Constant(None))

            cls_args.append(arg)

        return ast_function(
            "from_json",
            ast_args([ast.arg("cls", None), ast.arg("json", ast.Name("dict"))]),
            [ast.Return(ast_call("cls", cls_args))],
            returns=ast.Name(self.id),
            decorators=["classmethod"],
        )

    def create_object_to_json_function(self):
        json_values = []
        for attr in self.attributes:
            category = attr.category
            attr_value = ast.Attribute(ast.Name("self"), attr.name)

            if category.does_not_require_unparsing:
                json_val = attr_value
            elif attr.is_list_of_references:
                var_name = attr.name[0]

                if category.unparse_with_base_type:
                    items_base_type = JS_TYPE_TO_BUILTIN_MAP.get(
                        self.context.get_type_by_ref(attr.items.ref).type
                    )
                    json_val = ast_list_comp(
                        ast_call(items_base_type, var_name), var_name, attr_value
                    )
                elif category.unparse_with_to_json:
                    to_json_call = ast_call(
                        ast.Attribute(ast.Name(var_name), "to_json"), []
                    )
                    json_val = ast_list_comp(to_json_call, var_name, attr_value)
                else:
                    raise Exception(
                        f"Can't convert attribute to json: {self.context.domain_name}.{self.id}.{attr.name}"
                    )
            else:
                if category.unparse_with_base_type:
                    base_type = JS_TYPE_TO_BUILTIN_MAP.get(
                        self.context.get_type_by_ref(attr.ref).type
                    )
                    json_val = ast_call(ast.Name(base_type), [attr_value])
                elif category.unparse_with_to_json:
                    json_val = ast_call(ast.Attribute(attr_value, "to_json"), [])
                else:
                    raise Exception(
                        f"Can't convert attribute to json: {self.context.domain_name}.{self.id}.{attr.name}"
                    )

            if attr.optional and not category.does_not_require_unparsing:
                json_val = ast.IfExp(attr_value, json_val, ast.Constant(None))

            json_values.append(json_val)

        json = ast.Dict(
            [ast.Constant(a.name) for a in self.attributes],
            json_values,
        )

        if self.has_optional_attributes:
            self.context.require(".common", "filter_none")
            json = ast_call("filter_none", [json])

        return ast_function(
            "to_json",
            ast_args([ast.arg("self", None)]),
            [ast.Return(json)],
            returns=ast.Name("dict"),
        )

    def create_object_list_ast(self):
        body = [self.create_docstring(), self.create_object_list_from_json_function()]
        base = ast.Name(
            create_type_annotation(self.type, None, self.items, False, self.context)
        )

        return ast_classdef(self.id, body, [base])

    def create_object_list_from_json_function(self):
        items_type_name = self.context.get_type_by_ref(self.items.ref).create_reference(
            self.context
        )
        items = ast_list_comp(ast_call(items_type_name, [ast.Name("x")]), "x", "json")

        return ast_function(
            "from_json",
            ast_args([ast.arg("cls", None), ast.arg("json", ast.Name("dict"))]),
            [ast.Return(ast_call("cls", [items]))],
            ast.Name(self.id),
            ["classmethod"],
        )

    def create_docstring(self):
        lines = []

        if self.description:
            lines += self.description.split("\n")

        if self.attributes:
            lines.append("")
            lines.append("Attributes")
            lines.append("----------")

            for attr in self.attributes:
                lines += attr.to_docstring()

        return ast_docstring(lines)


@dataclass
class CDPCommand:
    name: str
    description: Optional[str]
    experimental: bool
    deprecated: bool
    parameters: list[CDPParameter]
    returns: list[CDPReturn]
    context: ModuleContext
    has_optional_params: bool

    @classmethod
    def from_json(cls, command: dict, context: ModuleContext):
        parameters = []
        has_optional_params = False
        for p in command.get("parameters", []):
            param = CDPParameter.from_json(p, context)
            parameters.append(param)
            if param.optional:
                has_optional_params = True

        parameters.sort(key=lambda p: p.optional)

        return cls(
            command["name"],
            command.get("description"),
            command.get("experimental", False),
            command.get("deprecated", False),
            parameters,
            [CDPReturn.from_json(r, context) for r in command.get("returns", [])],
            context,
            has_optional_params,
        )

    def to_ast(self):
        args = ast_args(
            [p.to_ast() for p in self.parameters],
            [ast.Constant(None) if p.optional else None for p in self.parameters],
        )

        body = [self.create_docstring()]

        method_params = ast.Dict(
            list(map(lambda param: ast.Str(param.name), self.parameters)),
            list(map(lambda param: ast.Name(param.name), self.parameters)),
        )
        method_dict = ast.Dict(
            [ast.Str("method"), ast.Str("params")],
            [ast.Str(f"{self.context.domain_name}.{self.name}"), method_params],
        )

        # Remove unset optional parameters from method dict
        if self.has_optional_params:
            self.context.require(".common", "filter_unset_parameters")
            method_dict = ast_call("filter_unset_parameters", [method_dict])

        body.append(ast.Return(method_dict))

        return ast_function(snake_case(self.name), args, body)

    def create_docstring(self):
        lines = []

        if self.description:
            lines += self.description.split("\n")

        if self.experimental:
            lines.append("")
            lines.append("**Experimental**")

        if self.deprecated:
            lines.append("")
            lines.append("**Deprectated**")

        if len(self.parameters) > 0:
            lines.append("")
            lines.append("Parameters")
            lines.append("----------")

            for param in self.parameters:
                lines += param.to_docstring()

        if len(self.returns) > 0:
            lines.append("")
            lines.append("Returns")
            lines.append("-------")

            for ret in self.returns:
                lines += ret.to_docstring()

        return ast_docstring(lines)


@dataclass
class CDPEvent:
    name: str
    description: Optional[str]
    deprecated: bool
    experimental: bool
    attributes: list[CDPAttribute]
    context: ModuleContext

    @classmethod
    def from_json(cls, event: dict, context: ModuleContext):
        attributes = event.get("parameters", [])
        if attributes:
            attributes = [CDPAttribute.from_json(p, context) for p in attributes]
            attributes.sort(
                key=lambda p: p.optional
            )  # Default value attributes after non-default attributes

        return cls(
            event["name"],
            event.get("description"),
            event.get("deprecated", False),
            event.get("experimental", False),
            attributes,
            context,
        )

    def to_ast(self):
        pass


@dataclass
class CDPDomain:
    domain: str
    description: Optional[str]
    experimental: bool
    dependencies: list[str]
    types: list[CDPType]
    commands: list[CDPCommand]
    events: list[CDPEvent]
    context: ModuleContext

    @classmethod
    def from_json(cls, domain: dict, context: ModuleContext) -> CDPDomain:
        domain_name = domain["domain"]
        types = domain.get("types", [])
        commands = domain.get("commands", [])
        events = domain.get("events", [])

        domain = cls(
            domain_name,
            domain.get("description"),
            domain.get("experimental", False),
            domain.get("dependencies", []),
            [CDPType.from_json(t, context) for t in types],
            [CDPCommand.from_json(c, context) for c in commands],
            [CDPEvent.from_json(e, context) for e in events],
            context,
        )

        # Register and return domain
        context.global_context.domains[domain_name] = domain
        return domain

    def to_ast(self):
        # Default imports
        imports = [
            ast_import_from("__future__", "annotations"),
            ast_import("dataclasses"),
        ]
        body = []

        for type in self.types:
            body.append(type.to_ast())

        for command in self.commands:
            body.append(command.to_ast())

        # Import dependencies
        for package, names in self.context.required_imports.items():
            if len(names) > 0:
                imports.append(ast_import_from(package, *names))
            else:
                imports.append(ast_import(package))

        return ast.Module(imports + body, lineno=0, col_offset=0, type_ignores=[])


def fetch_and_save_protocol(url: str, filename_template: str) -> tuple[int, int]:
    protocol = requests.get(url).json()

    minor = protocol["version"]["minor"]
    major = protocol["version"]["major"]

    filename = filename_template.format(major, minor)
    path = Path(GENERATE_DIR, filename)

    with path.open("w") as f:
        f.write(json.dumps(protocol, indent=4))

    return (major, minor)


def load_protocol(major: int, minor: int):
    browser_protocol_path = Path(
        GENERATE_DIR, BROWSER_PROTOCOL_FILENAME_TEMPLATE.format(major, minor)
    )
    with browser_protocol_path.open("r") as f:
        browser_protocol = json.loads(f.read())

    js_protocol_path = Path(
        GENERATE_DIR, JS_PROTOCOL_FILENAME_TEMPLATE.format(major, minor)
    )
    with js_protocol_path.open("r") as f:
        js_protocol = json.loads(f.read())

    # Combine and return protocols
    browser_protocol["domains"] += js_protocol["domains"]
    return browser_protocol


@app.command()
def generate(
    version: str,
    dry: bool = typer.Option(False, help="Do a dry run, don't generate anything"),
):
    # Parse version parameter
    version = version.replace("v", "")
    major, minor = version.split(".")

    logger.info(f"Generating protocol version {major}.{minor}")

    # Parse domains
    protocol = load_protocol(major, minor)
    global_context = GlobalContext()

    for domain_json in protocol["domains"]:
        domain_name = domain_json["domain"]
        module_context = ModuleContext(
            domain_to_module_name(domain_name), domain_name, global_context
        )
        domain = CDPDomain.from_json(domain_json, module_context)

        # logger.info(f"{domain.domain.ljust(20)}: {len(domain.types)} types, {len(domain.commands)} commands, {len(domain.events)} events")

    # Create domain modules
    output_dir = Path(GENERATE_DIR.parent, "cdpy")

    for domain in global_context.domains.values():
        output_path = Path(output_dir, domain.context.module_name + ".py")

        code = ast.unparse(domain.to_ast())
        if not dry:
            with output_path.open("w") as f:
                f.write(code)


@app.command()
def fetch():
    version = fetch_and_save_protocol(
        "https://raw.githubusercontent.com/ChromeDevTools/devtools-protocol/master/json/browser_protocol.json",
        BROWSER_PROTOCOL_FILENAME_TEMPLATE,
    )
    fetch_and_save_protocol(
        "https://raw.githubusercontent.com/ChromeDevTools/devtools-protocol/master/json/js_protocol.json",
        JS_PROTOCOL_FILENAME_TEMPLATE,
    )

    logger.info(f"Fetched protocol v{version[0]}.{version[1]}")


if __name__ == "__main__":
    app()
