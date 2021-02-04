import ast
import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

import astor
import inflection
import requests
import typer

GENERATE_DIR = script_dir = Path(os.path.abspath(os.path.split(__file__)[0]))
BROWSER_PROTOCOL_FILENAME_TEMPLATE = "browser_protocol-v{}.{}.json"
JS_PROTOCOL_FILENAME_TEMPLATE = "js_protocol-v{}.{}.json"

app = typer.Typer()

# Init logger
log_level = getattr(logging, os.environ.get("LOG_LEVEL", "info").upper())
logging.basicConfig(level=log_level)
logger = logging.getLogger(__name__)


def snake_case(string: str):
    return inflection.underscore(string)


def ast_import_from(module: str, *names):
    return ast.ImportFrom(module, [ast.Name(n) for n in names], level=0)


class ModuleContext:
    def __init__(self):
        self.domain = None
        self.defined_functions: List[str] = []

    @property
    def module_name(self):
        self.module_name = snake_case(self.domain)


@dataclass
class CDPItems:
    type: Optional[str]
    ref: Optional[str]

    @classmethod
    def from_json(cls, item: dict):
        return cls(
            item.get("type"),
            item.get("ref"),
        )


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

    @classmethod
    def from_json(cls, property: dict):
        items = property.get("items")

        return cls(
            property["name"],
            property.get("description"),
            property.get("type"),
            property.get("$ref"),
            property.get("enum"),
            CDPItems.from_json(items) if items else None,
            property.get("optional", False),
            property.get("experimental", False),
            property.get("deprecated", False),
        )


@dataclass
class CDPParameter(CDPProperty):
    def to_ast(self):
        return ast.arg(self.name, None)  # TODO Type Annotation


@dataclass
class CDPReturn(CDPProperty):
    pass


@dataclass
class CDPType:
    id: str
    description: Optional[str]
    type: str
    items: List[CDPItems]
    enum_values: Optional[List[str]]
    properties: Optional[List[CDPProperty]]

    @classmethod
    def from_json(cls, type_: dict):
        items = type_.get("items")
        properties = type_.get("properties")

        return cls(
            type_["id"],
            type_.get("description"),
            type_["type"],
            CDPItems.from_json(items) if items else None,
            type_.get("enum"),
            [CDPProperty.from_json(p) for p in properties] if properties else None,
        )


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
        parameters = command.get("parameters", [])
        returns = command.get("returns", [])

        return cls(
            command["name"],
            command.get("description"),
            command.get("experimental", False),
            command.get("deprecated", False),
            [CDPParameter.from_json(p) for p in parameters],
            [CDPReturn.from_json(r) for r in returns],
            context,
        )

    def to_ast(self):
        function_name = snake_case(self.name)
        self.context.defined_functions.append(function_name)

        args = ast.arguments(
            args=[p.to_ast() for p in self.parameters],
            vararg=None,
            kwarg=None,
            defaults=[
                ast.Name("NOT_SET") if p.optional else None for p in self.parameters
            ],
        )

        body = []

        # TODO docstring

        method_params = ast.Dict(
            list(map(lambda arg: ast.Str(arg.arg), args.args)),
            list(map(lambda arg: ast.Name(arg.arg), args.args)),
        )
        method_dict = ast.Dict(
            [ast.Str("method"), ast.Str("params")],
            [ast.Str("{}.{}".format(self.context.domain, self.name)), method_params],
        )

        body.append(ast.Return(method_dict))

        return ast.FunctionDef(
            function_name, args, body, decorator_list=[], lineno=0, col_offset=0
        )


@dataclass
class CDPEvent:
    name: str
    description: Optional[str]
    deprecated: bool
    experimental: bool
    parameters: List[CDPParameter]

    @classmethod
    def from_json(cls, event: dict):
        parameters = event.get("parameters", [])

        return cls(
            event["name"],
            event.get("description"),
            event.get("deprecated", False),
            event.get("experimental", False),
            [CDPParameter.from_json(p) for p in parameters],
        )

    def to_ast(self):
        pass  # TODO Event to ast


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

        context = ModuleContext()
        context.domain = domain_name

        return cls(
            domain_name,
            domain.get("description"),
            domain.get("experimental", False),
            domain.get("dependencies", []),
            [CDPType.from_json(t) for t in types],
            [CDPCommand.from_json(c, context) for c in commands],
            [CDPEvent.from_json(e) for e in events],
            context,
        )

    def to_ast(self):
        body = [ast_import_from("typing", "List", "Optional")]

        for command in self.commands:
            body.append(command.to_ast())

        return ast.Module(body, lineno=0, col_offset=0)


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

    for domain_json in protocol["domains"]:
        domain = CDPDomain.from_json(domain_json)


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
