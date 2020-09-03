from pathlib import Path

from packaging.version import Version

MARKER = ".. changelog start\n\n"


def update_changelog(changelog_file: Path, new_version: Version, body: str) -> None:
    changelog = changelog_file.read_text()
    prefix, marker, tail = changelog.partition(MARKER)
    if marker != MARKER:
        raise Exception()

    changelog_file.write_text(
        "".join(
            [
                prefix,
                marker,
                f"v{new_version}\n",
                "." * (1 + len(str(new_version))),
                "\n",
                body,
                "\n\n",
                tail,
            ]
        )
    )
