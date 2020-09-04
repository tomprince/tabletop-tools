import json
from pathlib import Path
from typing import Any, Dict, List

from .config import Config
from .utils.formats import format_json, to_unix


def _unpack_objects(objects: List[Dict[str, Any]], base_path: Path) -> None:
    index = []
    for obj in objects:
        guid = obj.pop("GUID")
        if not guid:
            raise Exception("Object does not have a GUID.")
        while guid in index:
            guid = "{:x}".format(int(guid, base=16) + 1)
            if len(guid) > 6:
                raise Exception("Invalid generated guid.")
        index.append(guid)
        path = base_path.joinpath(guid)
        path.mkdir(parents=True, exist_ok=True)
        obj_script = obj.pop("LuaScript")
        script_path = path.joinpath("script.lua")
        if obj_script.strip():
            script_path.write_text(to_unix(obj_script))
        elif script_path.exists():
            script_path.unlink()
        contained_objects = obj.pop("ContainedObjects", None)
        if contained_objects is not None:
            _unpack_objects(contained_objects, path.joinpath("contained"))
        path.joinpath("object.json").write_text(format_json(obj))
    if index:
        base_path.joinpath("index.list").write_text("\n".join(index) + "\n")


def unpack(*, savegame: Dict[str, Any], config: Config) -> None:
    global_script = to_unix(savegame.pop("LuaScript"))
    config.global_script.write_text(global_script)

    script_state = savegame.pop("LuaScriptState")
    if script_state:
        script_state = json.loads(script_state)
        config.script_state.write_text(format_json(script_state))
    else:
        config.script_state.unlink()

    note = savegame.pop("Note")
    config.note.write_text(note)

    xml_ui = to_unix(savegame.pop("XmlUI"))
    if xml_ui:
        config.xml_ui.write_text(xml_ui)
    else:
        config.xml_ui.unlink()

    _unpack_objects(savegame.pop("ObjectStates"), config.objects)

    config.savegame.write_text(format_json(savegame))
