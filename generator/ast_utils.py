import ast

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
