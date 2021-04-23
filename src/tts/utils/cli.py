# -*- coding: utf-8 -*-

# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at http://mozilla.org/MPL/2.0/.

import argparse
import logging
import sys
import traceback
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Protocol,
    Tuple,
    TypeVar,
    Union,
    cast,
)

import attr


class CommandType(Protocol):
    args: List[Tuple[Tuple[str, ...], Dict[str, Any]]]

    def __call__(self, *args: List[Any], **kwargs: Dict[str, Any]) -> None:
        ...


F = TypeVar("F", bound=Union[CommandType, Callable[..., None]])


class _HelpFormatter(argparse.HelpFormatter):
    def _fill_text(self, text: str, text_width: int, indent: str) -> str:
        paras = text.split("\n\n")
        _fill_text = super()._fill_text
        return "\n\n".join([_fill_text(para, text_width, indent) for para in paras])


@attr.s(cmp=False)
class CLI:
    description = attr.ib(type=str)
    _commands: List[
        Tuple[CommandType, str, Optional[str], Optional[str], Any, Any]
    ] = attr.ib(default=[], init=False)

    def command(
        self,
        name: str,
        help: Optional[str] = None,
        description: Optional[str] = None,
        **kwargs: Any,
    ) -> Callable[[F], F]:
        defaults = kwargs.pop("defaults", {})

        def decorator(func: F) -> F:
            self._commands.append(
                (cast(CommandType, func), name, help, description, kwargs, defaults)
            )
            return func

        return decorator

    @staticmethod
    def argument(*names: str, **kwargs: Any) -> Callable[[F], F]:
        def decorator(func: F) -> F:
            if not hasattr(func, "args"):
                func.args = []
            # Decorators run from bottom to top of the order they were
            # specified in the source. In order to make positional arguments
            # appear in the order they were specifed, we insert arguments at
            # the beginning, so that the list of arguments appears in the same
            # order they were specified in the source.
            func.args.insert(0, (names, kwargs))
            return func

        return decorator

    def create_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            description=self.description, formatter_class=_HelpFormatter
        )
        subparsers = parser.add_subparsers(dest="command")
        subparsers.required = True
        for (func, name, help, description, kwargs, defaults) in self._commands:
            if help and description:
                description = f"{help}\n\n{description}"
            subparser = subparsers.add_parser(
                name,
                help=help,
                description=description,
                **kwargs,
                formatter_class=_HelpFormatter,
            )
            for arg in getattr(func, "args", []):
                subparser.add_argument(*arg[0], **arg[1])
            subparser.set_defaults(command=func, **defaults)
        return parser

    def main(self) -> None:
        logging.basicConfig(
            format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
        )
        parser = self.create_parser()
        args = parser.parse_args()
        try:
            command = args.command
            del args.command
            command(**vars(args))
        except Exception:
            traceback.print_exc()
            sys.exit(1)
