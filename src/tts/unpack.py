import json
from typing import Any, Dict, List

from .savegame import UnpackedIndex, UnpackedObject, UnpackedSavegame


def _unpack_objects(
    objects: List[Dict[str, Any]],
    base_path: UnpackedIndex[UnpackedObject],
) -> None:
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
        unpacked_object = base_path.child(guid, create=True)

        obj_script = obj.pop("LuaScript")
        unpacked_object.script.write_text(obj_script)

        contained_objects = obj.pop("ContainedObjects", None)
        if contained_objects is not None:
            _unpack_objects(contained_objects, unpacked_object.contained)

        script_state = json.loads(obj.pop("LuaScriptState") or "null")
        unpacked_object.script_state.write_json(script_state)

        xml_ui = obj.pop("XmlUI", "")
        unpacked_object.xml_ui.write_text(xml_ui.strip())

        unpacked_object.object.write_json(obj)
    if index:
        base_path.write_index(index)


def unpack(*, savegame: Dict[str, Any], unpacked_savegame: UnpackedSavegame) -> None:
    script = savegame.pop("LuaScript").strip()
    unpacked_savegame.script.write_text(script)

    script_state = json.loads(savegame.pop("LuaScriptState") or "null")
    unpacked_savegame.script_state.write_json(script_state)

    note = savegame.pop("Note")
    unpacked_savegame.note.write_text(note)

    xml_ui = savegame.pop("XmlUI", "")
    unpacked_savegame.xml_ui.write_text(xml_ui.strip())

    _unpack_objects(savegame.pop("ObjectStates"), unpacked_savegame.objects)

    unpacked_savegame.savegame.write_json(savegame)
