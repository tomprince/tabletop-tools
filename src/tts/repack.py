from typing import Any, Dict, List

from .savegame import UnpackedIndex, UnpackedNote, UnpackedObject, UnpackedSavegame
from .utils.formats import dump_json


def _repack_objects(base_path: UnpackedIndex[UnpackedObject]) -> List[Dict[str, Any]]:
    objects = []
    for guid, unpacked_object in base_path.children():
        obj = unpacked_object.object.read_json()
        if obj is None:
            # TODO: give object path
            raise Exception(f"Couldn't find object with GUID {guid}.")
        obj["GUID"] = guid

        obj["LuaScript"] = unpacked_object.script.read_text()

        contained_objects = _repack_objects(unpacked_object.contained)
        if contained_objects:
            obj["ContainedObjects"] = contained_objects

        script_state = unpacked_object.script_state.read_json()
        if script_state is not None:
            obj["LuaScriptState"] = dump_json(script_state)
        else:
            obj["LuaScriptState"] = ""

        obj["XmlUI"] = unpacked_object.xml_ui.read_text()

        objects.append(obj)
    return objects


def _repack_notes(
    base_path: UnpackedIndex[UnpackedNote],
) -> Dict[str, Dict[str, Any]]:
    notes = {}
    for label, unpacked_note in base_path.children():
        note = unpacked_note.note.read_json(required=True)
        note["body"] = unpacked_note.text.read_text()

        notes[label] = note
    return notes


def repack(*, unpacked_savegame: UnpackedSavegame) -> Dict[str, Any]:
    savegame = unpacked_savegame.savegame.read_json()
    assert isinstance(savegame, dict)

    script = unpacked_savegame.script.read_text()
    savegame["LuaScript"] = script

    script_state = unpacked_savegame.script_state.read_json()
    if script_state is not None:
        savegame["LuaScriptState"] = dump_json(script_state)
    else:
        savegame["LuaScriptState"] = ""

    note = unpacked_savegame.note.read_text()
    savegame["Note"] = note

    notes = _repack_notes(unpacked_savegame.notes)
    if notes:
        if "TabStates" in savegame:
            raise Exception(
                f"Found both 'TabStates' in savegame, "
                f"and notes in '{unpacked_savegame.notes.path}'."
            )
        else:
            savegame["TabStates"] = notes

    savegame["XmlUI"] = unpacked_savegame.xml_ui.read_text()

    savegame["ObjectStates"] = _repack_objects(unpacked_savegame.objects)

    return savegame
