import json
from decimal import Decimal
from functools import partial
from typing import Any, Dict, Optional, cast

from ..config import Config


def to_unix(text: str) -> str:
    text = text.replace("\r\n", "\n")
    if text and not text.endswith("\n"):
        text += "\n"
    return text


def _quantize(val: Decimal) -> Decimal:
    return val.quantize(Decimal("0.0001"))


def _encode_decimal(obj: Any, config: Optional[Config] = None) -> Any:
    if isinstance(obj, Decimal):
        if config and config.quantize:
            obj = _quantize(obj)
        if obj.is_zero():
            obj = Decimal(0.0)
        return float(obj)
    raise TypeError(
        f"xxxObject of type {obj.__class__.__name__} " f"is not JSON serializable"
    )


def format_json(value: Dict[Any, Any], *, config: Config) -> str:
    return (
        json.dumps(
            value,
            indent=2,
            separators=(",", ": "),
            ensure_ascii=False,
            default=partial(_encode_decimal, config=config),
        )
        + "\n"
    )


def dump_json(value: Dict[Any, Any]) -> str:
    """
    Dump json in a format suitable for inclusion as a string in a packed savegame.
    """
    return json.dumps(value, ensure_ascii=False, default=_encode_decimal)


def _decode_decimal(val: str, *, config: Optional[Config]) -> Decimal:
    dec = Decimal(val)
    if config and config.quantize:
        dec = _quantize(dec)
    if dec.is_zero():
        return Decimal(0.0)
    return dec


def parse_json(value: str, *, config: Optional[Config] = None) -> Dict[Any, Any]:
    return cast(
        Dict[Any, Any],
        json.loads(value, parse_float=partial(_decode_decimal, config=config)),
    )
