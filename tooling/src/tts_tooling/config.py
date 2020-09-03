from pathlib import Path

import attr
import toml


@attr.s(auto_attribs=True, frozen=True)
class Config:
    project_root: Path
    release_file: Path
    changelog_file: Path
    package: Path
    version_module: Path


def parse_config(project_root: Path) -> Config:
    project_root = project_root.absolute()
    pyproject = toml.load(project_root.joinpath("pyproject.toml"))

    tool_config = pyproject["tool"]["tts_tooling"]
    release_file = project_root.joinpath(tool_config["release_file"])
    changelog = project_root.joinpath(tool_config["changelog"])

    package_name = pyproject["tool"]["flit"]["metadata"]["module"]
    package = project_root.joinpath("src", package_name)
    version_module = package.joinpath("__init__.py")

    return Config(
        project_root=project_root,
        release_file=release_file,
        changelog_file=changelog,
        package=package,
        version_module=version_module,
    )
