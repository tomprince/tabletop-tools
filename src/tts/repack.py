import json

from .utils.formats import format_json, to_win


def repack_objects(objects, base_path):
    index_path = base_path.joinpath("index.list")
    if not index_path.is_file():
        return
    index = index_path.read_text().splitlines()
    for guid in index:
        path = base_path.joinpath(guid)
        if not path.is_dir():
            raise Exception("Objects must be directories")
        obj = json.loads(path.joinpath("object.json").read_text())
        obj["GUID"] = guid
        script_path = path.joinpath("script.lua")
        if script_path.exists():
            obj["LuaScript"] = to_win(script_path.read_text())
        else:
            obj["LuaScript"] = ""
        if path.joinpath("contained").is_dir():
            obj["ContainedObjects"] = []
            repack_objects(obj["ContainedObjects"], path.joinpath("contained"))

        objects.append(obj)


def repack(*, savegame, config):
    game = json.loads(config.savegame.read_text())

    global_script = config.global_script.read_text()
    game["LuaScript"] = to_win(global_script)

    script_state = json.loads(config.script_state.read_text())
    game["LuaScriptState"] = json.dumps(script_state)

    note = config.note.read_text()
    game["Note"] = note

    xml_ui = config.xml_ui.read_text()
    game["XmlUI"] = to_win(xml_ui)

    game["ObjectStates"] = []
    repack_objects(game["ObjectStates"], config.objects)

    if not savegame.parent.exists():
        savegame.parent.mkdir(parents=True)
    savegame.write_text(format_json(game))
