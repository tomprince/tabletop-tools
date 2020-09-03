# -*- coding: utf-8 -*-

from pathlib import Path

from .utils.cli import CLI

app = CLI("Interact with Tabletop Simulator mods")


@app.command("unpack", help="Unpack a tts mod.")
@app.argument(
    "savegame",
    type=Path,
)
def unpack_cmd(*, savegame: Path) -> None:
    from .config import config
    from .unpack import unpack

    unpack(savegame=savegame, config=config)


@app.command("repack", help="Repack a tts mod.")
@app.argument(
    "savegame",
    type=Path,
    nargs="?",
    default="build/savegame.json",
)
def repack_cmd(*, savegame: Path) -> None:
    from .config import config
    from .repack import repack

    repack(savegame=savegame, config=config)


main = app.main
