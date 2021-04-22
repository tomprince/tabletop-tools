from __future__ import annotations

from typing import Callable, Optional, Type

import mypy
from mypy.nodes import ARG_POS, Argument, AssignmentStmt, NameExpr, Var
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


def layout_class_callback(ctx: ClassDefContext) -> None:
    path_type = ctx.api.builtin_type("pathlib.Path")
    config_type = ctx.api.named_type_or_none("tts.config.Config")  # type: ignore

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
        [
            Argument(Var("path"), path_type, None, ARG_POS),
            Argument(Var("config"), config_type, None, ARG_POS),
        ],
        NoneType(),
    )


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
