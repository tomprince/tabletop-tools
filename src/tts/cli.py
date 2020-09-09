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
)
@app.argument("--fileid", type=int, help="Workshop file id to unpack.")
@app.argument("--binary", action="store_true")
def repack_cmd(
    *, savegame_file: Optional[Path], fileid: Optional[int], binary: bool
) -> None:
    from .config import config
    from .repack import repack

    if fileid and savegame_file:
        raise Exception("Can't specify both a savegame file and a workshop file id.")
    elif fileid and binary:
        raise Exception("Can't specify both a workshop file id and '--binary'.")
    elif not savegame_file:
        if binary:
            savegame_file = Path("build/savegame.bson")
        else:
            savegame_file = Path("build/savegame.json")

    if not fileid and not savegame_file.parent.exists():
        savegame_file.parent.mkdir(parents=True)

    savegame = repack(config=config)

    if fileid:
        import bson

        from tts.steam import cli_login, update_file, upload_file

        client = cli_login()
        # It appears that tabletop simulator depends on the file being named
        # `WorkshopUpload`.
        upload_file(client, "WorkshopUpload", bson.dumps(savegame))
        update_file(client, fileid, "WorkshopUpload")

    elif binary:
        import bson

        savegame_file.write_bytes(bson.dumps(savegame))
    else:
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


@app.command(
    "workshop-upload",
    help="Upload a mod to the steam workshop.",
    description="This will currently only update a existing mod.",
)
@app.argument("fileid", type=int)
@app.argument(
    "savegame_file",
    metavar="savegame",
    type=Path,
)
def upload_cmd(*, fileid: int, savegame_file: Path) -> None:
    import bson

    from tts.steam import cli_login, update_file, upload_file

    savegame = json.loads(savegame_file.read_text())
    client = cli_login()
    # It appears that tabletop simulator depends on the file being named
    # `WorkshopUpload`.
    upload_file(client, "WorkshopUpload", bson.dumps(savegame))
    update_file(client, fileid, "WorkshopUpload")


main = app.main
