import json
from pathlib import Path
from typing import Any, Dict, List

from .config import Config


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


def repack(*, config: Config) -> Dict[str, Any]:
    savegame = json.loads(config.savegame.read_text())
    assert isinstance(savegame, dict)

    global_script = config.global_script.read_text()
    savegame["LuaScript"] = global_script

    if config.script_state.exists():
        script_state = json.loads(config.script_state.read_text())
        savegame["LuaScriptState"] = json.dumps(script_state)
    else:
        savegame["LuaScriptState"] = ""

    note = config.note.read_text()
    savegame["Note"] = note

    if config.xml_ui.exists():
        xml_ui = config.xml_ui.read_text()
        savegame["XmlUI"] = xml_ui
    else:
        savegame["XmlUI"] = ""

    savegame["ObjectStates"] = repack_objects(config.objects)

    return savegame
