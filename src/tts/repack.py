import json
from pathlib import Path
from typing import Any, Dict, List

from .config import Config
from .utils.formats import format_json


def repack_objects(base_path: Path) -> List[Dict[str, Any]]:
    objects = []
    index_path = base_path.joinpath("index.list")
    if not index_path.is_file():
        return []
    index = index_path.read_text().splitlines()
    for guid in index:
        path = base_path.joinpath(guid)
        if not path.is_dir():
            raise Exception("Objects must be directories")
        obj = json.loads(path.joinpath("object.json").read_text())
        obj["GUID"] = guid

        script_path = path.joinpath("script.lua")
        if script_path.exists():
            obj["LuaScript"] = script_path.read_text()
        else:
            obj["LuaScript"] = ""

        if path.joinpath("contained").is_dir():
            obj["ContainedObjects"] = repack_objects(path.joinpath("contained"))

        script_state_path = path.joinpath("script-state.json")
        if script_state_path.exists():
            script_state = json.loads(script_state_path.read_text())
            obj["LuaScriptState"] = json.dumps(script_state)
        else:
            obj["LuaScriptState"] = ""

        xml_ui_path = path.joinpath("ui.xml")
        if xml_ui_path.exists():
            obj["XmlUI"] = xml_ui_path.read_text()
        else:
            obj["XmlUI"] = ""

        objects.append(obj)
    return objects


def repack(*, savegame: Path, config: Config) -> None:
    game = json.loads(config.savegame.read_text())

    global_script = config.global_script.read_text()
    game["LuaScript"] = global_script

    if config.script_state.exists():
        script_state = json.loads(config.script_state.read_text())
        game["LuaScriptState"] = json.dumps(script_state)
    else:
        game["LuaScriptState"] = ""

    note = config.note.read_text()
    game["Note"] = note

    if config.xml_ui.exists():
        xml_ui = config.xml_ui.read_text()
        game["XmlUI"] = xml_ui
    else:
        game["XmlUI"] = ""

    game["ObjectStates"] = repack_objects(config.objects)

    if not savegame.parent.exists():
        savegame.parent.mkdir(parents=True)
    savegame.write_text(format_json(game))
