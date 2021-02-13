import ast
from os import O_APPEND, linesep
from typing import Iterable, Optional, Union


class DocstringBuilder(list):
    def __init__(self, line: Optional[str] = None, linesep="\n\t"):
        self._linesep = linesep

        if line != None:
            self.line(line)

    def section(self, name: str, entries: Iterable[str]):
        self.append("")
        self.append(name)
        self.append("-" * len(name))

        for e in entries:
            self += e

    def section_if(self, condition, name: str, entries: Iterable[str]):
        if condition:
            self.section(name, entries)
        return self

    def line(self, line: str = ""):
        if line != None:
            self += line.split("\n")
        return self

    def line_if(self, condition, line: str):
        if condition:
            self.line(line)
        return self

    def build(self):
        docstr = self._linesep.join(self)
        if len(self) > 1:
            docstr += "\n\t"
        return ast.Expr(ast.Constant(docstr))


def ast_from_str(expr: str):
    r = ast.parse(expr).body[0]

    if type(r) == ast.Expr:
        return r.value
    else:
        return r


def ast_import_from(module: str, *names):
    return ast.ImportFrom(module, [ast.alias(name=n) for n in names], level=0)


def ast_import(*modules: str):
    return ast.Import([ast.Name(m) for m in modules])


def ast_call(callable: Union[str, ast.AST], args: list[Union[str, ast.AST]]):
    if type(callable) == str:
        callable = ast.Name(callable)

    args = map(lambda a: ast.Name(a) if type(a) == str else a, args)

    return ast.Call(callable, list(args), [])


def ast_classdef(
    name: str,
    body: list[ast.AST],
    bases: list[Union[str, ast.AST]] = [],
    decorators: list[Union[str, ast.AST]] = [],
):

    bases = map(lambda b: ast.Name(b) if type(b) == str else b, bases)
    decorators = map(lambda d: ast.Name(d) if type(d) == str else d, decorators)

    return ast.ClassDef(
        name, bases=list(bases), body=body, decorator_list=list(decorators), keywords=[]
    )


def ast_args(args: list[ast.AST], defaults: list[ast.AST] = []):
    return ast.arguments(
        args=args,
        vararg=None,
        kwarg=None,
        defaults=defaults,
        posonlyargs=[],
        kwonlyargs=[],
    )


def ast_function(
    name: str,
    args: ast.arguments,
    body: list[ast.AST],
    returns=None,
    decorators: list[Union[str, ast.AST]] = [],
):
    decorators = map(lambda d: ast.Name(d) if type(d) == str else d, decorators)

    return ast.FunctionDef(
        name=name,
        args=args,
        body=body,
        decorator_list=list(decorators),
        returns=returns,
        lineno=0,
    )


def ast_module(body: list[ast.AST]):
    return ast.Module(body, lineno=0, col_offset=0, type_ignores=[])
