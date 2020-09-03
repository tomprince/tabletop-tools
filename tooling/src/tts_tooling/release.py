import enum
from pathlib import Path

import attr
import yaml


@enum.unique
class ReleaseType(enum.Enum):
    PATCH = "patch"
    MINOR = "minor"
    MAJOR = "major"


@attr.s(auto_attribs=True, frozen=True)
class Release:
    type: ReleaseType
    changelog_text: str


def parse_release(release_file: Path) -> Release:
    release = release_file.read_text()
    header, body = release.split("\n---\n", 1)
    attributes = yaml.safe_load(header)
    return Release(
        type=ReleaseType(attributes["type"]),
        changelog_text=body,
    )
