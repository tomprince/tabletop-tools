# -*- coding: utf-8 -*-

import json
from pathlib import Path
from typing import Optional

from .utils.cli import CLI
from .utils.formats import format_json

app = CLI("Interact with Tabletop Simulator mods")


@app.command("unpack", help="Unpack a tts mod.")
@app.argument(metavar="savegame", dest="savegame_file", type=Path, nargs="?")
@app.argument("--fileid", type=int, help="Workshop file id to unpack.")
def unpack_cmd(*, savegame_file: Optional[Path], fileid: Optional[int]) -> None:
    from .config import config
    from .unpack import unpack
    from .workshop import get_workshop_mod

    if savegame_file and fileid:
        raise Exception("Can't specify both a savegame file and a workshop file id.")
    elif savegame_file:
        savegame = json.loads(savegame_file.read_text())
    elif fileid:
        savegame = get_workshop_mod(fileid)
    else:
        raise Exception("Must specify a savegame file or workshop fileid.")

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


@app.command("workshop-download", help="Download a mod from the steam workshop.")
@app.argument("fileid", type=int)
@app.argument(
    "-o", type=Path, dest="output", help="File to write mod (default: <fileid>.json)"
)
def download_cmd(*, fileid: int, output: Optional[Path]) -> None:
    from .workshop import get_workshop_mod

    if output is None:
        output = Path(f"{fileid}.json")

    mod = get_workshop_mod(fileid)
    output.write_text(format_json(mod))


main = app.main
