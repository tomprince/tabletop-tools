from __future__ import annotations

from typing import Callable, Optional, Type

import mypy
from mypy.nodes import (
    ARG_POS,
    MDEF,
    Argument,
    AssignmentStmt,
    NameExpr,
    SymbolTableNode,
    Var,
)
from mypy.plugin import ClassDefContext, Plugin
from mypy.plugins.common import add_method
from mypy.types import NoneType


def _make_name_lvalue_var(
    lvalue: NameExpr, type: "mypy.types.Type", ctx: ClassDefContext
) -> Var:
    var = Var(lvalue.name, type)
    var.set_line(lvalue.line)
    var.is_ready = True
    var.info = ctx.cls.info
    return var


def add_var(ctx: ClassDefContext, name: str, type: "mypy.types.Type"):
    var = Var(name)
    var.info = ctx.cls.info
    var._fullname = f"{ctx.cls.info.fullname}.{name}"
    var.type = type
    ctx.cls.info.names[name] = SymbolTableNode(MDEF, var)


def layout_class_callback(ctx: ClassDefContext) -> None:
    path_type = ctx.api.builtin_type("pathlib.Path")

    # Change the types of class members when type checking the body to `pathlib.Path`.
    # `_unpacked_layout` expects the values to be paths.
    for stmt in ctx.cls.defs.body:
        assert isinstance(stmt, AssignmentStmt)
        assert len(stmt.lvalues) == 1
        lvalue = stmt.lvalues[0]
        assert isinstance(lvalue, NameExpr)

        lvalue.node = _make_name_lvalue_var(lvalue, path_type, ctx)

    add_method(
        ctx,
        "__init__",
        [Argument(Var("path"), path_type, None, ARG_POS)],
        NoneType(),
    )
    add_var(ctx, "path", path_type)


class LayoutPlugin(Plugin):
    def get_class_decorator_hook(
        self, fullname: str
    ) -> Optional[Callable[[ClassDefContext], None]]:
        if fullname == "tts.savegame._unpacked_layout":
            return layout_class_callback
        return None


def plugin(version: str) -> Type[LayoutPlugin]:
    # ignore version argument if the plugin works with all mypy versions.
    return LayoutPlugin
