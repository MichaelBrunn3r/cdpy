import ast
from typing import Union

import astor


def ast_args(args, defaults=[]):
    return ast.arguments(
        posonlyargs=[],
        args=args,
        kwonlyargs=None,
        vararg=None,
        kwarg=None,
        kw_defaults=None,
        defaults=defaults,
    )


def ast_from_str(expr: str):
    return ast.parse(expr).body[0]


def ast_import_from(module: str, *names):
    return ast.ImportFrom(module, [ast.alias(name=n) for n in names], level=0)


def ast_call(callable: str, args: list[ast.AST]):
    return ast.Call(ast.Name(callable), args, [])


def ast_list_comp(
    foreach: ast.AST, target: Union[str, ast.AST], iterable: Union[str, ast.AST]
):
    if type(target) == str:
        target = ast.Name(target)

    if type(iterable) == str:
        iterable = ast.Name(iterable)

    return ast.ListComp(foreach, [ast.comprehension(target, iterable, [])])


def ast_classdef(
    name: str,
    body: list[ast.AST],
    bases: list[Union[str, ast.AST]] = [],
    decorators: list[Union[str, ast.AST]] = [],
):
    for i, base in enumerate(bases):
        if type(base) == str:
            bases[i] == ast.Name(base)

    for i, decorator in enumerate(decorators):
        if type(decorator) == str:
            decorators[i] == ast.Name(decorator)

    return ast.ClassDef(name, bases=bases, body=body, decorator_list=decorators)
