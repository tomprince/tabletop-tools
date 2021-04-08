import json
from typing import Any, Dict, List

from .savegame import UnpackedIndex, UnpackedObject, UnpackedSavegame


def _repack_objects(base_path: UnpackedIndex[UnpackedObject]) -> List[Dict[str, Any]]:
    objects = []
    for guid, unpacked_object in base_path.children():
        obj = unpacked_object.object.read_json()
        if obj is None:
            raise Exception(
                f"Missing 'object.json' for object in '{unpacked_object.path}'."
            )
        obj["GUID"] = guid

        obj["LuaScript"] = unpacked_object.script.read_text()

        contained_objects = _repack_objects(unpacked_object.contained)
        if contained_objects:
            obj["ContainedObjects"] = contained_objects

        script_state = unpacked_object.script_state.read_json()
        if script_state is not None:
            obj["LuaScriptState"] = json.dumps(script_state)
        else:
            obj["LuaScriptState"] = ""

        obj["XmlUI"] = unpacked_object.xml_ui.read_text()

        objects.append(obj)
    return objects


def repack(*, unpacked_savegame: UnpackedSavegame) -> Dict[str, Any]:
    savegame = unpacked_savegame.savegame.read_json()
    assert isinstance(savegame, dict)

    script = unpacked_savegame.script.read_text()
    savegame["LuaScript"] = script

    script_state = unpacked_savegame.script_state.read_json()
    if script_state is not None:
        savegame["LuaScriptState"] = json.dumps(script_state)
    else:
        savegame["LuaScriptState"] = ""

    note = unpacked_savegame.note.read_text()
    savegame["Note"] = note

    savegame["XmlUI"] = unpacked_savegame.xml_ui.read_text()

    savegame["ObjectStates"] = _repack_objects(unpacked_savegame.objects)

    return savegame
