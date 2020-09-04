# -*- coding: utf-8 -*-

import json
from pathlib import Path

from .utils.cli import CLI
from .utils.formats import format_json

app = CLI("Interact with Tabletop Simulator mods")


@app.command("unpack", help="Unpack a tts mod.")
@app.argument(metavar="savegame", dest="savegame_file", type=Path, nargs="?")
def unpack_cmd(*, savegame_file: Path) -> None:
    from .config import config
    from .unpack import unpack

    savegame = json.loads(savegame_file.read_text())
    unpack(savegame=savegame, config=config)


@app.command("repack", help="Repack a tts mod.")
@app.argument(
    metavar="savegame",
    dest="savegame_file",
    type=Path,
    nargs="?",
    default="build/savegame.json",
)
def repack_cmd(*, savegame_file: Path) -> None:
    from .config import config
    from .repack import repack

    if not savegame_file.parent.exists():
        savegame_file.parent.mkdir(parents=True)

    savegame = repack(config=config)

    savegame_file.write_text(format_json(savegame))


main = app.main
