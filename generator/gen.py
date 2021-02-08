from __future__ import annotations

import ast
import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import astor
import inflection
import requests
import typer
from ast_utils import *

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
        self.required_domain_modules: set[str] = set()

    def require_domain_module(self, module_name: str):
        """Signals the context that a module needs to be imported"""
        self.required_domain_modules.add(module_name)

    def get_type_by_ref(self, reference: str) -> CDPType | None:
        domain_name, type_name = get_reference_parts(reference)
        if not domain_name:
            domain_name = self.domain_name

        return self.global_context.get_type_by_ref(domain_name + "." + type_name)


def domain_to_module_name(domain: str):
    return snake_case(domain)


def snake_case(string: str):
    return inflection.underscore(string)


def javascript_type_to_ast(type: str):
    """Converts a javascript type to a python type ast node"""
    return ast.Name(JS_TYPE_TO_BUILTIN_MAP.get(type, type))


def domain_type_reference_to_ast(ref: str, context: ModuleContext):
    """Converts a reference to a domain type to a python type reference ast node"""
    referenced_domain, referenced_type = get_reference_parts(ref)

    if not referenced_domain or referenced_domain == context.domain_name:
        # References type in current domain -> module can be omitted
        return ast.Name(referenced_type)
    else:
        referenced_module = domain_to_module_name(referenced_domain)
        context.require_domain_module(referenced_module)
        return ast.Name(referenced_module + "." + referenced_type)


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

    def to_ast(self):
        if self.type:
            return javascript_type_to_ast(self.type)
        else:
            return domain_type_reference_to_ast(self.ref, self.context)


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
    def is_primitive(self):
        """Checks if the property is a primitive type (e.g. int, str, float, ...)"""
        return self.type and not self.items and not self.enum_values

    @property
    def is_primitive_list(self):
        """Checks if the property is a list of primitive types (e.g. list[int], list[str], list[float], ...)"""
        return self.items and self.items.type

    @property
    def is_enum(self):
        """Checks if the property is an enum"""
        # TODO not handled yet
        return self.enum_values

    @property
    def is_simple_type_reference(self):
        """Checks if the property references a simple type, i.e. a type that inherits from a primitive type.
        (e.g. class Simple(int))
        """
        if not self.ref:
            return False

        ref_type = self.context.get_type_by_ref(self.ref)

        return ref_type.is_simple or ref_type.is_simple_list

    @property
    def is_simple_type_reference_list(self):
        """Checks if the property is a list of references to a simple type, i.e. a type that inherits from a primitive type.
        (e.g. class Simple(int) -> list[Simple])
        """
        if not self.is_list_of_references:
            return False

        items_type = self.context.get_type_by_ref(self.items.ref)

        return self.is_list_of_references and (
            items_type.is_simple or items_type.is_simple_list
        )

    @property
    def is_enum_reference(self):
        """Checks if the property references an enum"""
        return self.ref and self.context.get_type_by_ref(self.ref).is_enum

    @property
    def is_enum_reference_list(self):
        """Checks if the property is a list of enum references"""
        return (
            self.is_list_of_references
            and self.context.get_type_by_ref(self.items.ref).is_enum
        )

    @property
    def is_complex_type_reference(self):
        """Checks if the property references a complex type, i.e. a type that has attributes."""
        return self.ref and self.context.get_type_by_ref(self.ref).is_complex

    @property
    def is_complex_type_reference_list(self):
        """Checks if the property i a list of references to a complex type, i.e. a type that has attributes."""
        return (
            self.is_list_of_references
            and self.context.get_type_by_ref(self.items.ref).is_complex
        )

    @property
    def is_list_of_references(self):
        """Checks if the property is a list and its items are references to an type"""
        return self.items and self.items.ref

    @classmethod
    def from_json(cls, property: dict, context: ModuleContext):
        items = property.get("items")

        return cls(
            property["name"],
            property.get("description"),
            property.get("type"),
            property.get("$ref"),
            property.get("enum"),
            CDPItems.from_json(items, context) if items else None,
            property.get("optional", False),
            property.get("experimental", False),
            property.get("deprecated", False),
            context,
        )

    def to_ast(self):
        annotation = self.create_type_annotation()
        if self.optional:
            annotation = ast.Subscript(ast.Name("Optional"), ast.Index(annotation))

        return ast.arg(self.name, annotation)

    def to_docstring(self):
        lines = [
            astor.to_source(self.to_ast())
            .replace('"', "")
            .replace("'", "")
            .replace("\n", "")
        ]
        if self.description and not self.description.isspace():
            lines += map(lambda l: "\t" + l, self.description.split("\n"))
        return lines

    def create_type_annotation(self):
        if self.type:
            type = javascript_type_to_ast(self.type)
        else:
            type = domain_type_reference_to_ast(self.ref, self.context)

        if self.items:
            type = ast.Subscript(type, ast.Index(self.items.to_ast()))
        return type


@dataclass
class CDPParameter(CDPProperty):
    pass


@dataclass
class CDPReturn(CDPProperty):
    pass


@dataclass
class CDPAttribute(CDPProperty):
    def to_ast(self):
        attr = ast.AnnAssign(
            ast.Name(self.name), self.create_type_annotation(), value=None, simple=1
        )

        if self.optional:
            attr.annotation = ast.Subscript(
                ast.Name("Optional"), ast.Index(attr.annotation)
            )
            attr.value = ast.Constant(None)

        return attr


@dataclass
class CDPType:
    id: str
    description: Optional[str]
    type: str
    items: CDPItems
    enum_values: Optional[list[str]]
    attributes: Optional[list[CDPAttribute]]
    context: ModuleContext

    @property
    def is_simple(self) -> bool:
        """Predicate wether this type is a simple type, i.e. it inherits from a primitive type (e.g. int, string, dict, ...)"""
        return not self.attributes and not self.items and not self.enum_values

    @property
    def is_simple_list(self) -> bool:
        """Predicate wether this type is a simple list, i.e. a list of primitives (e.g. list[int])"""
        return self.items and self.items.type

    @property
    def is_enum(self) -> bool:
        """Predicate wether this type is an enum"""
        return self.enum_values

    @property
    def is_complex(self) -> bool:
        """Predicate wether this type is complex, i.e. it has attributes"""
        return self.attributes

    @property
    def is_complex_list(self) -> bool:
        """Predicate wether this type is complex list, i.e. a list of complex or simple types (e.g. class CompList(list[simple]))"""
        if not self.items:
            return False

        if self.items.type:
            return False
        else:
            items_type = self.context.get_type_by_ref(self.items.ref)
            return items_type.is_complex or items_type.is_simple

    @classmethod
    def from_json(cls, json: dict, context: ModuleContext):
        items = json.get("items")
        attributes = json.get("properties")
        if attributes:
            attributes = [CDPAttribute.from_json(p, context) for p in attributes]
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
        )

    def to_ast(self):
        if self.is_simple or self.is_simple_list:
            return self.create_simple_ast()
        elif self.is_enum:
            return self.create_enum_ast()
        elif self.is_complex:
            return self.create_complex_ast()
        elif self.is_complex_list:
            return self.create_complex_list_ast()
        else:
            raise Exception(
                f"Can't generate AST for type '{self.context.domain_name}.{self.id}'"
            )

    def create_simple_ast(self):
        """Create the AST for a simple type"""

        # Add docstring
        body = [ast.Expr(ast.Str(self.create_docstring()))]

        body.append(self.create_simple_repr_function())

        base = javascript_type_to_ast(self.type)

        if self.items:
            if self.items.type:
                items_type = javascript_type_to_ast(self.items.type)
            else:
                items_type = javascript_type_to_ast(self.items.ref)

            base = ast.Subscript(base, javascript_type_to_ast(items_type))

        return ast.ClassDef(
            self.id,
            [base],
            body=body,
            decorator_list=[],
        )

    def create_simple_repr_function(self):
        """Create the __repr__ function for a simple type"""
        return ast.FunctionDef(
            "__repr__",
            ast_args([ast.arg("self", None)]),
            [ast_from_str(f"return f'{self.id}({{super().__repr__()}})'")],
            [],
        )

    def create_enum_ast(self):
        """Create the AST for an enum type"""
        body = [ast.Expr(ast.Str(self.create_docstring()))]

        # Add enum values
        for v in self.enum_values:
            body.append(ast.Assign([ast.Name(snake_case(v).upper())], ast.Str(v)))

        return ast.ClassDef(
            self.id, bases=[ast.Name("enum.Enum")], body=body, decorator_list=[]
        )

    def create_complex_ast(self):
        body = [ast.Expr(ast.Str(self.create_docstring()))]

        for attr in self.attributes:
            body.append(attr.to_ast())
        body.append(self.create_complex_from_json_function())

        return ast.ClassDef(
            self.id,
            bases=[ast.Name("Type")],
            body=body,
            decorator_list=[ast.Name("dataclasses.dataclass")],
        )

    def create_complex_from_json_function(self):
        cls_args = []
        for attr in self.attributes:
            attr_json_value = ast.Subscript(ast.Name("json"), ast.Constant(attr.name))

            if attr.is_primitive or attr.is_primitive_list:
                if attr.optional:
                    arg = ast.Attribute(
                        ast.Name("json"),
                        ast.Call(ast.Name("get"), [ast.Str(attr.name)], []),
                    )
                else:
                    arg = attr_json_value
            elif attr.is_enum:
                # TODO case not handled
                # logger.warn(f"1. Couldn't create argument: {self.context.domain_name}.{self.id}.{attr.name}")
                continue
            elif attr.is_list_of_references:
                items_type = self.context.get_type_by_ref(attr.items.ref)

                # If the referenced type is from another module, add that module before the type name
                if items_type.context.domain_name != self.context.domain_name:
                    items_type_name = (
                        items_type.context.module_name + "." + items_type.id
                    )
                else:
                    items_type_name = items_type.id

                target = ast.Name("x")
                if attr.is_simple_type_reference_list or attr.is_enum_reference_list:
                    arg = ast.ListComp(
                        ast.Call(ast.Name(items_type_name), [target], []),
                        [ast.comprehension(target, attr_json_value, [])],
                    )
                elif attr.is_complex_type_reference_list:
                    # print(f"{self.context.domain_name}.{self.id}.{attr.name}")
                    from_json_call = ast.Attribute(
                        ast.Name(items_type_name),
                        ast.Call(ast.Name("from_json"), [target], []),
                    )
                    arg = ast.ListComp(
                        from_json_call, [ast.comprehension(target, attr_json_value, [])]
                    )
                else:
                    logger.warning(
                        f"2. Couldn't create argument: {self.context.domain_name}.{self.id}.{attr.name}, {attr.items.ref}"
                    )
                    continue
            else:
                referenced_type = self.context.get_type_by_ref(attr.ref)

                # If the referenced type is from another module, add that module before the type name
                if referenced_type.context.domain_name != self.context.domain_name:
                    referenced_type_name = (
                        referenced_type.context.module_name + "." + referenced_type.id
                    )
                else:
                    referenced_type_name = referenced_type.id

                if attr.is_simple_type_reference or attr.is_enum_reference:
                    arg = ast.Call(
                        ast.Name(referenced_type_name), [attr_json_value], []
                    )
                elif attr.is_complex_type_reference:
                    arg = ast.Attribute(
                        ast.Name(referenced_type_name),
                        ast.Call(ast.Name("from_json"), [attr_json_value], []),
                    )
                else:
                    logger.warning(
                        f"3. Couldn't create argument: {self.context.domain_name}.{self.id}.{attr.name}, {attr.ref}"
                    )
                    continue

            # Wrap argument in 'if ... else None' if the attribute is optional.
            # Primitives are calling 'dict.get()' instead.
            if attr.optional and not attr.is_primitive and not attr.is_primitive_list:
                is_in_json_condition = ast.Compare(
                    ast.Constant(attr.name), [ast.In()], [ast.Name("json")]
                )
                arg = ast.IfExp(is_in_json_condition, arg, ast.Constant(None))

            cls_args.append(arg)

        return ast.FunctionDef(
            "from_json",
            ast_args([ast.arg("cls", None), ast.arg("json", ast.Name("dict"))]),
            [ast.Return(ast.Call(ast.Name("cls"), cls_args, []))],
            [ast.Name("classmethod")],
            ast.Name(self.id),
        )

    def create_complex_list_ast(self):
        body = [ast.Expr(ast.Str(self.create_docstring()))]

        body.append(self.create_complex_list_from_json_function())

        items_type = domain_type_reference_to_ast(self.items.ref, self.context)
        base = ast.Subscript(ast.Name("list"), javascript_type_to_ast(items_type))

        return ast.ClassDef(
            self.id,
            bases=[base],
            body=body,
            decorator_list=[],
        )

    def create_complex_list_from_json_function(self):
        items_type = self.context.get_type_by_ref(self.items.ref)

        # If the referenced type is from another module, add that module before the type name
        if items_type.context.domain_name != self.context.domain_name:
            items_type_name = items_type.context.module_name + "." + items_type.id
        else:
            items_type_name = items_type.id

        items = ast.ListComp(
            ast.Call(ast.Name(items_type_name), [ast.Name("x")], []),
            [ast.comprehension(ast.Name("x"), ast.Name("json"), [])],
        )

        return ast.FunctionDef(
            "from_json",
            ast_args([ast.arg("cls", None), ast.arg("json", ast.Name("dict"))]),
            [ast.Return(ast.Call(ast.Name("cls"), [items], []))],
            [ast.Name("classmethod")],
            ast.Name(self.id),
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

        docstr = "\n\t".join(lines)
        if len(lines) > 1:
            docstr += "\n\t"
        return docstr


@dataclass
class CDPCommand:
    name: str
    description: Optional[str]
    experimental: bool
    deprecated: bool
    parameters: list[CDPParameter]
    returns: list[CDPReturn]
    context: ModuleContext

    @classmethod
    def from_json(cls, command: dict, context: ModuleContext):
        parameters = [
            CDPParameter.from_json(p, context) for p in command.get("parameters", [])
        ]
        parameters.sort(key=lambda p: p.optional)
        returns = command.get("returns", [])

        return cls(
            command["name"],
            command.get("description"),
            command.get("experimental", False),
            command.get("deprecated", False),
            parameters,
            [CDPReturn.from_json(r, context) for r in returns],
            context,
        )

    def to_ast(self):
        args = ast.arguments(
            args=[p.to_ast() for p in self.parameters],
            vararg=None,
            kwarg=None,
            defaults=[
                ast.Constant(None) if p.optional else None for p in self.parameters
            ],
        )

        body = [ast.Expr(ast.Str(self.create_docstring()))]

        method_params = ast.Dict(
            list(map(lambda param: ast.Str(param.name), self.parameters)),
            list(map(lambda param: ast.Name(param.name), self.parameters)),
        )
        method_dict = ast.Dict(
            [ast.Str("method"), ast.Str("params")],
            [ast.Str(f"{self.context.domain_name}.{self.name}"), method_params],
        )

        # Remove unset parameters from method dict.
        # Only if method has optional parameters.
        if len(self.parameters) > 0 and self.parameters[-1].optional:
            method_dict = ast.Call(
                ast.Name("filter_unset_parameters"), [method_dict], []
            )

        body.append(ast.Return(method_dict))

        return ast.FunctionDef(
            snake_case(self.name), args, body, decorator_list=[], lineno=0, col_offset=0
        )

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

        docstr = "\n\t".join(lines)
        if len(lines) > 1:
            docstr += "\n\t"
        return docstr


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
    def from_json(cls, domain: dict, context: ModuleContext):
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
        imports = [
            ast_import_from("__future__", "annotations"),
            ast.Import([ast.Name("enum")]),
            ast.Import([ast.Name("dataclasses")]),
            ast_import_from("typing", "Optional"),
            ast_import_from(".common", "filter_unset_parameters", "Type"),
        ]
        body = []

        for type in self.types:
            body.append(type.to_ast())

        for command in self.commands:
            body.append(command.to_ast())

        if len(self.context.required_domain_modules) > 0:
            imports.append(ast_import_from(".", *self.context.required_domain_modules))

        return ast.Module(imports + body, lineno=0, col_offset=0)


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
def generate(version: str):
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
        CDPDomain.from_json(domain_json, module_context)

    # Create domain modules
    output_dir = Path(GENERATE_DIR.parent, "cdpy")

    for domain in global_context.domains.values():
        output_path = Path(output_dir, domain.context.module_name + ".py")
        with output_path.open("w") as f:
            f.write(astor.to_source(domain.to_ast()))


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
