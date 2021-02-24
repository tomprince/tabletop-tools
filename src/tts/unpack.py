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
            script_path.write_text(to_unix(obj_script), encoding="utf-8")
        elif script_path.exists():
            script_path.unlink()

        contained_objects = obj.pop("ContainedObjects", None)
        if contained_objects is not None:
            _unpack_objects(contained_objects, path.joinpath("contained"))

        script_state = obj.pop("LuaScriptState", "null")
        script_state_path = path.joinpath("script-state.json")
        if script_state:
            script_state = json.loads(script_state)
            script_state_path.write_text(format_json(script_state), encoding="utf-8")
        elif script_state_path.exists():
            script_state_path.unlink()

        xml_ui = obj.pop("XmlUI", None)
        xml_ui_path = path.joinpath("ui.xml")
        if xml_ui:
            xml_ui_path.write_text(to_unix(xml_ui), encoding="utf-8")
        elif xml_ui_path.exists():
            xml_ui_path.unlink()

        path.joinpath("object.json").write_text(format_json(obj), encoding="utf-8")
    if index:
        base_path.joinpath("index.list").write_text(
            "\n".join(index) + "\n", encoding="utf-8"
        )


def unpack(*, savegame: Dict[str, Any], config: Config) -> None:
    script = to_unix(savegame.pop("LuaScript"))
    config.script.write_text(script, encoding="utf-8")

    script_state = savegame.pop("LuaScriptState")
    if script_state:
        script_state = json.loads(script_state)
        config.script_state.write_text(format_json(script_state), encoding="utf-8")
    else:
        config.script_state.unlink()

    note = savegame.pop("Note")
    config.note.write_text(note, encoding="utf-8")

    xml_ui = to_unix(savegame.pop("XmlUI"))
    if xml_ui:
        config.xml_ui.write_text(xml_ui, encoding="utf-8")
    else:
        config.xml_ui.unlink()

    _unpack_objects(savegame.pop("ObjectStates"), config.objects)

    config.savegame.write_text(format_json(savegame), encoding="utf-8")
