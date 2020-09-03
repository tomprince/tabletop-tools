from pathlib import Path
from typing import List

from tts_tooling.changelog import update_changelog
from tts_tooling.config import parse_config
from tts_tooling.release import parse_release
from tts_tooling.vcs import commit
from tts_tooling.version import update_version


def main(args: List[str]) -> None:
    project_root = Path(args[0])
    config = parse_config(project_root)

    release = parse_release(config.release_file)
    new_version = update_version(config.version_module, release.type)
    update_changelog(config.changelog_file, new_version, release.changelog_text)

    config.release_file.unlink()

    commit(
        project_root,
        f"Bump version v{new_version} and update changelog.",
        [
            config.changelog_file,
            config.release_file,
            config.version_module,
        ],
    )


if __name__ == "__main__":
    import sys

    main(sys.argv[1:])
