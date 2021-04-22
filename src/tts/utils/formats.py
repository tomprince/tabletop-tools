import json
from typing import Any, Dict, cast


def to_unix(text: str) -> str:
    text = text.replace("\r\n", "\n")
    if text and not text.endswith("\n"):
        text += "\n"
    return text


def format_json(value: Dict[Any, Any]) -> str:
    return (
        json.dumps(value, indent=2, separators=(",", ": "), ensure_ascii=False) + "\n"
    )


def dump_json(value: Dict[Any, Any]) -> str:
    """
    Dump json in a format suitable for inclusion as a string in a packed savegame.
    """
    return json.dumps(value, ensure_ascii=False)


def parse_json(value: str) -> Dict[Any, Any]:
    return cast(Dict[Any, Any], json.loads(value))
