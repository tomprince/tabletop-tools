import json


def to_unix(text):
    return text.replace("\r\n", "\n")


def to_win(text):
    return text.replace("\n", "\r\n")


def format_json(value):
    return json.dumps(value, indent=2, separators=(",", ": "))
