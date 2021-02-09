import ast
from typing import Union


def ast_from_str(expr: str):
    return ast.parse(expr).body[0]


def ast_import_from(module: str, *names):
    return ast.ImportFrom(module, [ast.alias(name=n) for n in names], level=0)


def ast_import(*modules: str):
    return ast.Import([ast.Name(m) for m in modules])


def ast_call(callable: Union[str, ast.AST], args: list[Union[str, ast.AST]]):
    if type(callable) == str:
        callable = ast.Name(callable)

    args = map(lambda a: ast.Name(a) if type(a) == str else a, args)

    return ast.Call(callable, list(args), [])


def ast_list_comp(
    foreach: ast.AST, target: Union[str, ast.AST], iterable: Union[str, ast.AST]
):
    if type(target) == str:
        target = ast.Name(target)

    if type(iterable) == str:
        iterable = ast.Name(iterable)

    return ast.ListComp(
        foreach, [ast.comprehension(target, iterable, [], is_async=False)]
    )


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


def ast_docstring(lines: list[str]):
    docstr = "\n\t".join(lines)
    if len(lines) > 1:
        docstr += "\n\t"
    return ast.Expr(ast.Constant(docstr))


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
