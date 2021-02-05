import ast
import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Set, Tuple

import astor
import inflection
import requests
import typer

GENERATE_DIR = script_dir = Path(os.path.abspath(os.path.split(__file__)[0]))
BROWSER_PROTOCOL_FILENAME_TEMPLATE = "browser_protocol-v{}.{}.json"
JS_PROTOCOL_FILENAME_TEMPLATE = "js_protocol-v{}.{}.json"

JS_TO_PYTHON_TYPE_MAP = {
    "string": "str",
    "integer": "int",
    "number": "float",
    "boolean": "bool",
    "array": "List",
}

app = typer.Typer()

# Init logger
log_level = getattr(logging, os.environ.get("LOG_LEVEL", "info").upper())
logging.basicConfig(level=log_level)
logger = logging.getLogger(__name__)


def snake_case(string: str):
    return inflection.underscore(string)


def ast_import_from(module: str, *names):
    return ast.ImportFrom(module, [ast.Name(n) for n in names], level=0)


def parse_type_annotation(
    type: Optional[str], ref: Optional[str], context: "ModuleContext"
):
    if not type and not ref:
        raise Exception("At least one of 'type' or 'ref' must be not be None")

    if type:
        return ast.Name(JS_TO_PYTHON_TYPE_MAP.get(type, type))
    elif ref:
        parts = ref.split(".")
        referenced_domain, referenced_type = (
            parts if len(parts) > 1 else (None, parts[0])
        )

        # References type from foreign or current domain?
        if referenced_domain and referenced_domain != context.domain:
            referenced_module = ModuleContext.domain_to_module_name(referenced_domain)
            context.referenced_cdp_modules.add(referenced_module)
            return ast.Str(referenced_module + "." + referenced_type)
        else:
            if referenced_type in context.defined_types:
                return ast.Name(referenced_type)
            else:
                return ast.Str(referenced_type)


class ModuleContext:
    def __init__(self, domain: str):
        self.domain = domain
        self.module_name = ModuleContext.domain_to_module_name(self.domain)

        self.defined_functions: Set[str] = set()
        self.referenced_cdp_modules: Set[str] = set()
        self.defined_types: Set[str] = set()

    @classmethod
    def domain_to_module_name(cls, domain: str):
        return snake_case(domain)


@dataclass
class CDPItems:
    type: Optional[str]
    ref: Optional[str]
    context: ModuleContext

    @classmethod
    def from_json(cls, item: dict, context: ModuleContext):
        return cls(item.get("type"), item.get("$ref"), context)

    def to_ast(self):
        return parse_type_annotation(self.type, self.ref, self.context)


@dataclass
class CDPProperty:
    name: str
    description: Optional[str]
    type: Optional[str]
    ref: Optional[str]
    enum_values: Optional[List[str]]
    items: Optional[CDPItems]
    optional: bool
    experimental: bool
    deprecated: bool
    context: ModuleContext

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
        type = parse_type_annotation(self.type, self.ref, self.context)
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
    items: List[CDPItems]
    enum_values: Optional[List[str]]
    attributes: Optional[List[CDPAttribute]]
    context: ModuleContext

    @classmethod
    def from_json(cls, type_: dict, context: ModuleContext):
        items = type_.get("items")
        attributes = type_.get("properties")
        if attributes:
            attributes = [CDPAttribute.from_json(p, context) for p in attributes]
            attributes.sort(
                key=lambda p: p.optional
            )  # Default value attributes after non-default attributes

        return cls(
            type_["id"],
            type_.get("description"),
            type_["type"],
            CDPItems.from_json(items, context) if items else None,
            type_.get("enum"),
            attributes,
            context,
        )

    def to_ast(self):
        body = [ast.Expr(ast.Str(self.create_docstring()))]

        if self.attributes:
            for attr in self.attributes:
                body.append(attr.to_ast())

        self.context.defined_types.add(self.id)

        return ast.ClassDef(self.id, [], body=body, decorator_list=[])

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
    parameters: List[CDPParameter]
    returns: List[CDPReturn]
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
        function_name = snake_case(self.name)
        self.context.defined_functions.add(function_name)

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
            [ast.Str("{}.{}".format(self.context.domain, self.name)), method_params],
        )

        body.append(ast.Return(method_dict))

        return ast.FunctionDef(
            function_name, args, body, decorator_list=[], lineno=0, col_offset=0
        )

    def create_docstring(self):
        lines = []

        if self.description:
            lines.append(self.description)

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

        return "\n\t".join(lines)


@dataclass
class CDPEvent:
    name: str
    description: Optional[str]
    deprecated: bool
    experimental: bool
    attributes: List[CDPAttribute]
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
    dependencies: List[str]
    types: List[CDPType]
    commands: List[CDPCommand]
    events: List[CDPEvent]
    context: ModuleContext

    @classmethod
    def from_json(cls, domain: dict):
        domain_name = domain["domain"]
        types = domain.get("types", [])
        commands = domain.get("commands", [])
        events = domain.get("events", [])

        context = ModuleContext(domain_name)

        return cls(
            domain_name,
            domain.get("description"),
            domain.get("experimental", False),
            domain.get("dependencies", []),
            [CDPType.from_json(t, context) for t in types],
            [CDPCommand.from_json(c, context) for c in commands],
            [CDPEvent.from_json(e, context) for e in events],
            context,
        )

    def to_ast(self):
        imports = [ast_import_from("typing", "List", "Optional")]
        body = []

        for type in self.types:
            body.append(type.to_ast())

        for command in self.commands:
            body.append(command.to_ast())

        if len(self.context.referenced_cdp_modules) > 0:
            imports.append(ast_import_from(".", *self.context.referenced_cdp_modules))

        return ast.Module(imports + body, lineno=0, col_offset=0)


def fetch_and_save_protocol(url: str, filename_template: str) -> Tuple[int, int]:
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

    logger.info("Generating protocol version {}.{}".format(major, minor))

    protocol = load_protocol(major, minor)

    # Create domain modules
    output_dir = Path(GENERATE_DIR.parent, "cdpy")
    for domain_json in protocol["domains"]:
        domain = CDPDomain.from_json(domain_json)

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

    logger.info("Fetched protocol v{}.{}".format(version[0], version[1]))


if __name__ == "__main__":
    app()
