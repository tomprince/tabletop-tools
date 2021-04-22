from __future__ import annotations

from pathlib import Path

import attr
import cattr
import toml

CONFIG_NAME = Path("tabletop-tools.toml")


@attr.resolve_types
@attr.s(auto_attribs=True)
class Config:
    quantize: bool = False

    @classmethod
    def load(cls, config_file: Path) -> Config:
        if config_file.exists():
            return cattr.structure(
                toml.loads(config_file.read_text(encoding="utf-8")), cls
            )
        else:
            return Config()
