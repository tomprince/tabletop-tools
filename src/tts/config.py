from pathlib import Path

import attr


@attr.s(auto_attribs=True)
class Config:
    savegame: Path
    script: Path
    script_state: Path
    note: Path
    objects: Path
    xml_ui: Path


config = Config(
    savegame=Path("savegame.json"),
    script=Path("script.lua"),
    script_state=Path("script-state.json"),
    note=Path("note.txt"),
    xml_ui=Path("ui.xml"),
    objects=Path("objects"),
)
