import json
from typing import Any, Dict


def to_unix(text: str) -> str:
    return text.replace("\r\n", "\n")


def to_win(text: str) -> str:
    return text.replace("\n", "\r\n")


def format_json(value: Dict[Any, Any]) -> str:
    return json.dumps(value, indent=2, separators=(",", ": "))
