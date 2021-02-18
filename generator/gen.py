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
    def __init__(self, protocol_version: str):
        self.domains: dict[str, Domain] = {}
        self.protocol_version = protocol_version

    def get_type_by_ref(self, reference: str) -> Type | None:
        domain_name, type_name = get_reference_parts(reference)
        domain = self.domains[domain_name]
        for type_ in domain.types:
            if type_.id == type_name:
                return type_

    def register_domain(self, name: str, domain: Domain):
        self.domains[name] = domain


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

    def get_type_by_ref(self, reference: str) -> Type | None:
        domain_name, type_name = get_reference_parts(reference)
        if not domain_name:
            domain_name = self.domain_name

        return self.global_context.get_type_by_ref(domain_name + "." + type_name)


def domain_to_module_name(domain: str):
    return snake_case(domain)


def snake_case(string: str):
    return inflection.underscore(string)


def create_type_annotation(
    type, ref, is_list: bool, optional: bool, context: ModuleContext
):
    if type:
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

    if is_list:
        annot = f"list[{annot}]"

    if optional:
        annot = f"Optional[{annot}]"

    return annot


def get_reference_parts(reference: str) -> tuple[Optional[str], str]:
    """Splits a reference into a domain and a name part"""
    parts = reference.split(".")
    return tuple(parts) if len(parts) > 1 else (None, parts[0])


@dataclass
class Items:
    json_type: Optional[str]
    ref: Optional[str]
    context: ModuleContext

    @classmethod
    def from_json(cls, json: dict, context: ModuleContext):
        return cls(json.get("type"), json.get("$ref"), context)

    @property
    def type(self):
        return create_type_annotation(
            self.json_type, self.ref, False, False, self.context
        )


class PropertyCategory(enum.Enum):
    BUILTIN = 0
    BUILTIN_LIST = 1
    TYPELESS_ENUM = 2
    SIMPLE = 3
    SIMPLE_LIST = 4
    ENUM = 5
    ENUM_LIST = 6
    OBJECT = 7
    OBJECT_LIST = 8

    @classmethod
    def from_cdp_type(cls, type: Type, is_list: bool):
        """Returns a category according to a properties type"""
        if is_list:
            return {
                TypeCategory.BUILTIN: PropertyCategory.SIMPLE_LIST,
                TypeCategory.BUILTIN_LIST: PropertyCategory.SIMPLE_LIST,
                TypeCategory.ENUM: PropertyCategory.ENUM_LIST,
                TypeCategory.OBJECT: PropertyCategory.OBJECT_LIST,
                TypeCategory.OBJECT_LIST: PropertyCategory.OBJECT_LIST,
            }.get(type.category)
        else:
            return {
                TypeCategory.BUILTIN: PropertyCategory.SIMPLE,
                TypeCategory.BUILTIN_LIST: PropertyCategory.SIMPLE,
                TypeCategory.ENUM: PropertyCategory.ENUM,
                TypeCategory.OBJECT: PropertyCategory.OBJECT,
            }.get(type.category)

    @property
    def does_not_require_parsing(self):
        return self in (self.BUILTIN, self.BUILTIN_LIST, self.TYPELESS_ENUM)

    @property
    def parse_with_from_json(self):
        """Wether the types of this category should be parsed with a from_json call (e.g. SomeType.from_json(json))"""
        return self in (self.OBJECT, self.OBJECT_LIST)

    @property
    def does_not_require_unparsing(self):
        return self.does_not_require_parsing

    @property
    def unparse_with_to_json(self):
        return self.parse_with_from_json

    @property
    def unparse_with_attribute_value(self):
        return self in (self.ENUM, self.ENUM_LIST)


@dataclass
class Property:
    name: str
    description: Optional[str]
    json_type: Optional[str]
    ref: Optional[str]
    enum_values: Optional[list[str]]
    items: Optional[Items]
    optional: bool
    experimental: bool
    deprecated: bool
    context: ModuleContext

    @classmethod
    def from_json(cls, json: dict, context: ModuleContext) -> Property:
        items = json.get("items")
        optional = json.get("optional", False)
        if optional:
            context.require("typing", "Optional")

        return cls(
            json["name"],
            json.get("description"),
            json.get("type"),
            json.get("$ref"),
            json.get("enum"),
            Items.from_json(items, context) if items else None,
            optional,
            json.get("experimental", False),
            json.get("deprecated", False),
            context,
        )

    @property
    def is_list(self):
        return self.items != None

    @property
    def default_value(self) -> ast.AST | None:
        return ast.Constant(None) if self.optional else None

    def type(self, annotated=False):
        if self.is_list:
            type, ref = self.items.json_type, self.items.ref
        else:
            type, ref = self.json_type, self.ref

        return create_type_annotation(
            type, ref, self.is_list, annotated and self.optional, self.context
        )

    @property
    def type_annotation(self):
        return self.type(True)

    @property
    def category(self):
        if not hasattr(self, "_category"):
            if self.is_list:
                if self.items.json_type:
                    self._category = PropertyCategory.BUILTIN_LIST
                else:
                    items_type = self.context.get_type_by_ref(self.items.ref)
                    self._category = PropertyCategory.from_cdp_type(items_type, True)
            elif self.enum_values:
                self._category = PropertyCategory.TYPELESS_ENUM
            elif self.ref:
                ref_type = self.context.get_type_by_ref(self.ref)
                self._category = PropertyCategory.from_cdp_type(ref_type, False)
            elif self.json_type:
                self._category = PropertyCategory.BUILTIN
            else:
                raise Exception("Can't determin property type")

        return self._category

    def to_ast(self):
        return ast.arg(self.name, ast.Name(self.type_annotation))

    def create_parse_from_ast(self, from_dict):
        value = f"{from_dict}['{self.name}']"

        if self.category.does_not_require_parsing:
            if self.optional:
                code = f"{from_dict}.get('{self.name}')"
            else:
                code = value
        else:
            if self.is_list:
                base_type = self.items.type
            else:
                base_type = self.type()

            if self.category.parse_with_from_json:
                parse_template = f"{base_type}.from_json({{}})"
            else:
                parse_template = f"{base_type}({{}})"

            if self.is_list:
                elem = self.name[0]
                code = f"[{parse_template.format(elem)} for {elem} in {value}]"
            else:
                code = parse_template.format(value)

            if self.optional:
                code = f"{code} if '{self.name}' in {from_dict} else None"

        return ast_from_str(code)

    def create_unparse_from_ast(self, from_value: str):
        if self.category.does_not_require_unparsing:
            code = from_value
        else:
            if self.category.unparse_with_attribute_value:
                unparse_template = f"{{}}.value"
            elif self.category.unparse_with_to_json:
                unparse_template = f"{{}}.to_json()"
            else:
                base_type = JS_TYPE_TO_BUILTIN_MAP.get(
                    self.context.get_type_by_ref(
                        self.items.ref if self.is_list else self.ref
                    ).json_type
                )
                unparse_template = f"{base_type}({{}})"

            if self.is_list:
                elem = self.name[0]
                code = f"[{unparse_template.format(elem)} for {elem} in {from_value}]"
            else:
                code = unparse_template.format(from_value)

            if self.optional and not self.category.does_not_require_unparsing:
                code = f"{code} if {from_value} else None"

        return code

    def to_docstring(self):
        lines = [f"{self.name}: {self.type_annotation}"]

        if self.description and not self.description.isspace():
            lines += map(lambda l: "\t" + l, self.description.split("\n"))
        return lines


@dataclass
class Attribute(Property):
    def to_ast(self):
        value = (
            ast.Constant(None) if self.optional else None
        )  # Default value if optional
        return ast.AnnAssign(
            ast.Name(self.name), ast.Name(self.type_annotation), value=value, simple=1
        )


class TypeCategory(enum.Enum):
    BUILTIN = 0
    BUILTIN_LIST = 1
    ENUM = 2
    OBJECT = 3
    OBJECT_LIST = 4


@dataclass
class Type:
    id: str
    description: Optional[str]
    json_type: str
    items: Items
    enum_values: Optional[list[str]]
    attributes: Optional[list[Attribute]]
    context: ModuleContext
    has_optional_attributes: bool

    @classmethod
    def from_json(cls, json: dict, context: ModuleContext):
        has_optional_attributes = False
        items = json.get("items")

        attributes = json.get("properties")
        if attributes:
            for i, attr_json in enumerate(attributes):
                attr = Attribute.from_json(attr_json, context)
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
            Items.from_json(items, context) if items else None,
            json.get("enum"),
            attributes,
            context,
            has_optional_attributes,
        )

    @property
    def category(self) -> TypeCategory:
        if not hasattr(self, "_category"):
            if self.items:
                if self.items.json_type:
                    self._category = TypeCategory.BUILTIN_LIST
                else:
                    self._category = TypeCategory.OBJECT_LIST
            elif self.enum_values:
                self._category = TypeCategory.ENUM
            elif self.attributes:
                self._category = TypeCategory.OBJECT
            else:
                self._category = TypeCategory.BUILTIN

        return self._category

    def create_reference(self, from_context: ModuleContext):
        """Create a reference to this type from a context"""
        if self.context != from_context:
            return f"{self.context.module_name}.{self.id}"
        else:
            return self.id

    @property
    def base(self) -> str:
        if not hasattr(self, "_base"):
            if self.category == TypeCategory.BUILTIN:
                self._base = create_type_annotation(
                    self.json_type, None, False, False, self.context
                )
            elif self.category == TypeCategory.ENUM:
                self.context.require("enum", None)
                self._base = "enum.Enum"
            elif self.category in [TypeCategory.BUILTIN_LIST, TypeCategory.OBJECT_LIST]:
                self._base = f"list[{self.items.type}]"
            else:
                self._base = "object"
        return self._base

    @property
    def decorators(self):
        if self.category == TypeCategory.OBJECT:
            return ["dataclasses.dataclass"]
        else:
            return []

    def to_ast(self):
        body = [self.create_docstring()]

        if self.category in [TypeCategory.BUILTIN, TypeCategory.BUILTIN_LIST]:
            body.append(self.create_builtin_repr_function())
        elif self.category == TypeCategory.ENUM:
            for v in self.enum_values:
                body.append(ast_from_str(f'{snake_case(v).upper()} = "{v}"'))
        elif self.category == TypeCategory.OBJECT:
            for attr in self.attributes:
                body.append(attr.to_ast())
            body.append(self.create_object_from_json_function())
            body.append(self.create_object_to_json_function())
        elif self.category == TypeCategory.OBJECT_LIST:
            body.append(self.create_object_list_from_json_function())
            body.append(self.create_object_list_to_json_function())
        else:
            raise Exception(
                f"Can't generate AST for type '{self.context.domain_name}.{self.id}'"
            )

        return ast_classdef(
            self.id, body, [self.base] if self.base != "object" else [], self.decorators
        )

    def create_builtin_repr_function(self):
        """Create the __repr__ function for a simple type"""
        return ast_function(
            "__repr__",
            ast_args([ast.arg("self", None)]),
            [ast_from_str(f"return f'{self.id}({{super().__repr__()}})'")],
        )

    def create_object_from_json_function(self):
        cls_args = []
        for attr in self.attributes:
            cls_args.append(attr.create_parse_from_ast("json"))

        return ast_function(
            "from_json",
            ast_args([ast.arg("cls", None), ast.arg("json", ast.Name("dict"))]),
            [ast.Return(ast_call("cls", cls_args))],
            returns=ast.Name(self.id),
            decorators=["classmethod"],
        )

    def create_object_to_json_function(self):
        json = ast.Dict(
            [ast.Constant(a.name) for a in self.attributes],
            [
                ast_from_str(a.create_unparse_from_ast(f"self.{a.name}"))
                for a in self.attributes
            ],
        )

        if self.has_optional_attributes:
            self.context.require("._utils", "filter_none")
            json = ast_call("filter_none", [json])

        return ast_function(
            "to_json",
            ast_args([ast.arg("self", None)]),
            [ast.Return(json)],
            returns=ast.Name("dict"),
        )

    def create_object_list_from_json_function(self):
        items_type = self.context.get_type_by_ref(self.items.ref)
        type_name = items_type.create_reference(self.context)

        if items_type.category == TypeCategory.BUILTIN:
            items = f"[{type_name}(e) for e in json]"
        else:
            raise Exception(
                f"Can't create from_json function for {self.context.module_name}.{self.id}. Not implemented yet"
            )

        return ast_function(
            "from_json",
            ast_args([ast.arg("cls", None), ast.arg("json", ast.Name("dict"))]),
            [ast_from_str(f"return cls({items})")],
            ast.Name(self.id),
            ["classmethod"],
        )

    def create_object_list_to_json_function(self):
        items_type = self.context.get_type_by_ref(self.items.ref)

        if items_type.category == TypeCategory.BUILTIN:
            items = f"[{items_type.base}(e) for e in self]"
        else:
            raise Exception(
                f"Can't create to_json function for {self.context.module_name}.{self.id}. Not implemented yet"
            )

        return ast_function(
            "to_json",
            ast_args([ast.arg("self", None)]),
            [ast_from_str(f"return {items}")],
            returns=ast.Name("dict"),
        )

    def create_docstring(self):
        docstr = DocstringBuilder(self.description)

        if self.attributes:
            docstr.section(
                "Attributes", map(lambda a: a.to_docstring(), self.attributes)
            )

        return docstr.build()


@dataclass
class Method:
    name: str
    description: Optional[str]
    experimental: bool
    deprecated: bool
    parameters: list[Property]
    returns: Optional[list[Property]]
    context: ModuleContext
    has_optional_params: bool

    @classmethod
    def from_json(cls, json: dict, context: ModuleContext):
        parameters = []
        has_optional_params = False
        for p in json.get("parameters", []):
            param = Property.from_json(p, context)
            parameters.append(param)
            if param.optional:
                has_optional_params = True

        parameters.sort(key=lambda p: p.optional)

        return cls(
            json["name"],
            json.get("description"),
            json.get("experimental", False),
            json.get("deprecated", False),
            parameters,
            [Property.from_json(r, context) for r in json["returns"]]
            if "returns" in json
            else None,
            context,
            has_optional_params,
        )

    def to_ast(self):
        args = ast_args(
            [p.to_ast() for p in self.parameters],
            [p.default_value for p in self.parameters],
        )

        body = [self.create_docstring()]

        if self.returns:
            # Yield method json and receive response json
            body.append(ast_from_str(f"response = yield {self.method_json_ast()}"))

            self.context.require("typing", "Generator")
            if len(self.returns) == 1:
                ret = self.returns[0]
                response = ret.create_parse_from_ast("response")
                function_type = f"Generator[dict,dict,{ret.type_annotation}]"
            else:
                response = ast.Dict(
                    [ast.Constant(r.name) for r in self.returns],
                    [r.create_parse_from_ast("response") for r in self.returns],
                )
                function_type = "Generator[dict,dict,dict]"

            # Return parsed response
            body.append(ast.Return(response))
        else:
            body.append(ast_from_str(f"return {self.method_json_ast()}"))
            function_type = "dict"

        decorators = []
        if self.deprecated:
            self.context.require("deprecated.sphinx", "deprecated")
            decorators.append(
                ast_from_str(
                    f"deprecated(version={self.context.global_context.protocol_version})"
                )
            )

        return ast_function(
            snake_case(self.name),
            args,
            body,
            returns=ast.Name(function_type),
            decorators=decorators,
        )

    def method_json_ast(self):
        params = [
            f'"{p.name}": {p.create_unparse_from_ast(p.name)}' for p in self.parameters
        ]
        params = "{" + ",".join(params) + "}"

        # Remove unset optional parameters
        if self.has_optional_params:
            self.context.require("._utils", "filter_none")
            params = f"filter_none({params})"

        return f'{{"method": "{self.context.domain_name}.{self.name}", "params": {params}}}'

    def create_docstring(self):
        docstr = DocstringBuilder(self.description)

        if len(self.parameters) > 0:
            docstr.section(
                "Parameters", map(lambda p: p.to_docstring(), self.parameters)
            )

        if self.returns:
            docstr.section("Returns", map(lambda r: r.to_docstring(), self.returns))

        if self.experimental:
            docstr.line("\n**Experimental**")

        return docstr.build()


@dataclass
class Event:
    name: str
    description: Optional[str]
    deprecated: bool
    experimental: bool
    attributes: list[Attribute]
    context: ModuleContext

    @classmethod
    def from_json(cls, json: dict, context: ModuleContext):
        attributes = json.get("parameters", [])
        if attributes:
            attributes = [Attribute.from_json(p, context) for p in attributes]
            attributes.sort(
                key=lambda p: p.optional
            )  # Default value attributes after non-default attributes

        return cls(
            json["name"],
            json.get("description"),
            json.get("deprecated", False),
            json.get("experimental", False),
            attributes,
            context,
        )

    @property
    def classname(self):
        return self.name[0].capitalize() + self.name[1:]

    def to_ast(self):
        body = [self.create_docstring()]

        for attr in self.attributes:
            body.append(attr.to_ast())

        body.append(self.create_from_json_function())

        self.context.require("dataclasses", None)
        return ast_classdef(
            self.classname,
            body,
            decorators=["dataclasses.dataclass"],
        )

    def create_from_json_function(self):
        cls_args = []
        for attr in self.attributes:
            cls_args.append(attr.create_parse_from_ast("json"))

        return ast_function(
            "from_json",
            ast_args([ast.arg("cls", None), ast.arg("json", ast.Name("dict"))]),
            [ast.Return(ast_call("cls", cls_args))],
            returns=ast.Name(self.classname),
            decorators=["classmethod"],
        )

    def create_docstring(self):
        docstr = DocstringBuilder(self.description)

        if self.attributes:
            docstr.section(
                "Attributes", map(lambda a: a.to_docstring(), self.attributes)
            )

        return docstr.build()


@dataclass
class Domain:
    domain: str
    description: Optional[str]
    experimental: bool
    dependencies: list[str]
    types: list[Type]
    methods: list[Method]
    events: list[Event]
    context: ModuleContext

    @classmethod
    def from_json(cls, json: dict, context: ModuleContext) -> Domain:
        domain_name = json["domain"]
        types = json.get("types", [])
        methods = json.get("commands", [])
        events = json.get("events", [])

        return cls(
            domain_name,
            json.get("description"),
            json.get("experimental", False),
            json.get("dependencies", []),
            [Type.from_json(t, context) for t in types],
            [Method.from_json(m, context) for m in methods],
            [Event.from_json(e, context) for e in events],
            context,
        )

    def to_ast(self):
        # Default imports
        imports = [
            ast_import_from("__future__", "annotations"),
            ast_import("dataclasses"),
        ]
        body = []

        for type in self.types:
            body.append(type.to_ast())

        for m in self.methods:
            body.append(m.to_ast())

        for event in self.events:
            body.append(event.to_ast())

        # Import dependencies
        for package, names in self.context.required_imports.items():
            if len(names) > 0:
                imports.append(ast_import_from(package, *names))
            else:
                imports.append(ast_import(package))

        return ast_module(imports + body)


def fetch_and_save_protocol(url: str, filename_template: str) -> tuple[int, int]:
    protocol = requests.get(url).json()

    minor = protocol["version"]["minor"]
    major = protocol["version"]["major"]

    filename = filename_template.format(major, minor)
    path = Path(GENERATE_DIR, filename)

    with path.open("w") as f:
        f.write(json.dumps(protocol, indent=4))

    return (major, minor)


def load_domains(major: int, minor: int):
    domain_files = [
        BROWSER_PROTOCOL_FILENAME_TEMPLATE.format(major, minor),
        JS_PROTOCOL_FILENAME_TEMPLATE.format(major, minor),
    ]
    domains = []
    for part in domain_files:
        with Path(GENERATE_DIR, part).open("r") as f:
            domains += json.loads(f.read())["domains"]

    return domains


def create_init_module(global_context: GlobalContext):
    body = []
    all = []

    # Import domain modules
    body.append(
        ast_import_from(
            ".", *[d.context.module_name for d in global_context.domains.values()]
        )
    )
    all += [f'"{d.context.module_name}"' for d in global_context.domains.values()]

    # Imports from cdpy
    cdpy_module_imports = ["parse_event", "EventParserError"]
    body.append(ast_import_from("._cdpy", *cdpy_module_imports))
    all += map(lambda i: f'"{i}"', cdpy_module_imports)

    # Add __all__ assignment
    body.append(ast_from_str(f"__all__ = [{','.join(all)}]"))

    return ast_module(body)


def create_event_parsers_module(global_context: GlobalContext):
    referenced_domain_modules = set()
    event_names = []
    event_parsers = []
    for domain in global_context.domains.values():
        for event in domain.events:
            event_names.append(
                ast.Constant(f"{event.context.domain_name}.{event.name}")
            )
            event_parsers.append(
                ast.Name(f"{event.context.module_name}.{event.classname}")
            )
            referenced_domain_modules.add(event.context.module_name)

    body = [
        ast_import_from(".", *list(referenced_domain_modules)),
        ast.Assign(
            [ast.Name("event_parsers")], ast.Dict(event_names, event_parsers), lineno=0
        ),
    ]

    return ast_module(body)


@app.command()
def generate(
    version: str,
    dry: bool = typer.Option(False, help="Do a dry run, don't generate anything"),
):
    # Load protocol
    version = version.replace("v", "")
    major, minor = version.split(".")
    domains = load_domains(major, minor)
    logger.info(f"Generating protocol version {major}.{minor}")

    # Parse protocol
    global_context = GlobalContext(f"{major}.{minor}")
    for domain_json in domains:
        domain_name = domain_json["domain"]
        module_context = ModuleContext(
            domain_to_module_name(domain_name), domain_name, global_context
        )
        domain = Domain.from_json(domain_json, module_context)
        global_context.register_domain(domain_name, domain)

    module_files: dict[str, str] = {}

    # Generate domain modules
    for domain in global_context.domains.values():
        module_files[domain.context.module_name + ".py"] = ast.unparse(domain.to_ast())
    logger.info(f"Generated {len(global_context.domains)} domains")

    # Generate Init module
    module_files["__init__.py"] = ast.unparse(create_init_module(global_context))

    # Generate event_parsers module
    module_files["_event_parsers.py"] = ast.unparse(
        create_event_parsers_module(global_context)
    )

    # Write files to disk
    if not dry:
        logger.info(f"Writing {len(module_files)} files ...")
        for path, content in module_files.items():
            with Path(GENERATE_DIR.parent, "cdpy", path).open("w") as f:
                f.write(content)


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
