from functools import partial
from pathlib import Path
from typing import Callable, Union

import libcst as cst
from libcst import matchers as m
from packaging.version import Version

from .release import ReleaseType


class VersionTransformer(m.MatcherDecoratableTransformer):
    new_version: Union[None, Version] = None

    def __init__(self, version_mod: Callable[[Version], Version]):
        super().__init__()
        self.version_mod = version_mod

    @m.call_if_inside(
        m.Assign(
            targets=[m.AssignTarget(target=m.Name("__version__"))],
            value=m.SimpleString(),
        )
    )
    @m.leave(m.SimpleString())
    def update_version(
        self, original_node: cst.SimpleString, updated_node: cst.SimpleString
    ) -> cst.SimpleString:
        if self.new_version:
            raise Exception("Multiple versions found.")

        old_version = Version(updated_node.evaluated_value)
        self.new_version = self.version_mod(old_version)
        return updated_node.with_changes(value=repr(str(self.new_version)))


def next_major(version: Version) -> Version:
    return Version(f"{version.major + 1}.0.0")


def next_minor(version: Version) -> Version:
    return Version(f"{version.major}.{version.minor + 1}.0")


def next_patch(version: Version) -> Version:
    return Version(f"{version.major}.{version.minor}.{version.micro + 1}")


next_fns = {
    ReleaseType.MAJOR: next_major,
    ReleaseType.MINOR: next_minor,
    ReleaseType.PATCH: next_patch,
}


def next_version(version: Version, release_type: ReleaseType) -> Version:
    return next_fns[release_type](version)


def update_version(module_path: Path, release_type: ReleaseType) -> Version:
    module = cst.parse_module(module_path.read_text())
    transformer = VersionTransformer(
        version_mod=partial(next_version, release_type=release_type)
    )
    module = module.visit(transformer)

    if transformer.new_version is None:
        raise Exception(f"Did not find a version to update in '{module_path}'.")

    module_path.write_text(module.code)

    return transformer.new_version
