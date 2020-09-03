import subprocess
from pathlib import Path
from typing import List, cast


def git_commit(project_root: Path, message: str, changed_files: List[Path]) -> None:
    subprocess.run(
        ["git", "commit", "-m", message] + cast(List[str], changed_files),
        cwd=project_root,
    )


def hg_commit(project_root: Path, message: str, changed_files: List[Path]) -> None:
    subprocess.run(
        ["hg", "commit", "-m", message, "--addremove"] + cast(List[str], changed_files),
        cwd=project_root,
    )


def commit(project_root: Path, message: str, changed_files: List[Path]) -> None:
    if project_root.joinpath(".hg").exists():
        hg_commit(project_root, message, changed_files)
    elif project_root.joinpath(".git").exists():
        git_commit(project_root, message, changed_files)
    else:
        raise Exception("Unknown version control system.")
