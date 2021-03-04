import json
from typing import Any, Dict


def to_unix(text: str) -> str:
    text = text.replace("\r\n", "\n")
    if text and not text.endswith("\n"):
        text += "\n"
    return text


def format_json(value: Dict[Any, Any]) -> str:
    return (
        json.dumps(value, indent=2, separators=(",", ": "), ensure_ascii=False) + "\n"
    )
