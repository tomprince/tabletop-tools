from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, TypedDict, cast

import attr
from node_vm2 import NodeVM, VMServer


class _BundleVM:
    # https://github.com/Benjamin-Dobell/luabundle#unbundled-data
    Metadata = TypedDict(
        "Metadata",
        {
            # "identifiers" -- omitted
            "luaVersion": str,
            "rootModuleName": str,
            "version": str,
        },
    )
    Module = TypedDict(
        "Module",
        {
            "name": str,
            "content": str,
            # "start": FilePosition,
            # "end": FilePosition,
        },
    )
    UnbundledData = TypedDict(
        "UnbundledData",
        {
            "metadata": Metadata,
            "modules": Dict[str, Module],
        },
    )

    def __init__(self) -> None:
        self._server: VMServer = VMServer()
        self._server.start()
        self._vm: NodeVM = NodeVM(self._server)
        self._vm.create()
        self._module = self._vm.run(
            Path(__file__).with_name("luabundle.js").read_text()
        )

    def __del__(self) -> None:
        self._vm.destroy()
        self._server.close()

    def write_file(self, name: str, script: str) -> None:
        self._module.call_member("writeFile", name, script)

    def unbundle_string(self, script: str) -> UnbundledData:
        return cast(
            _BundleVM.UnbundledData, self._module.call_member("unbundleString", script)
        )

    def bundle(self, script: str) -> str:
        return cast(
            str,
            self._module.call_member(
                "bundleString",
                script,
                {
                    "luaVersion": "5.2",
                    "isolate": True,
                    "paths": ["?"],
                    "metadata": True,
                },
            ),
        )


@attr.s(auto_attribs=True)
class Bundler:
    module_dir: Path
    _vm: _BundleVM = attr.ib(init=False, default=attr.Factory(_BundleVM))

    def __attrs_post_init__(self) -> None:
        if self.module_dir.exists():
            for module in self.module_dir.iterdir():
                if module.is_file() and module.suffix == ".lua":
                    self._vm.write_file(module.stem, module.read_text(encoding="utf-8"))

    def bundle(self, lua_script: str) -> str:
        return self._vm.bundle(lua_script)


@attr.s(auto_attribs=True)
class Unbundler:
    module_dir: Path
    modules: Dict[str, Any] = attr.ib(init=False, default=attr.Factory(dict))
    _vm: _BundleVM = attr.ib(init=False, default=attr.Factory(_BundleVM))

    def unbundle(self, lua_script: str) -> str:
        if not lua_script.startswith("-- Bundled by luabundle "):
            return lua_script

        unbundled = self._vm.unbundle_string(lua_script)
        root_module = unbundled["modules"].pop(unbundled["metadata"]["rootModuleName"])
        for name, module in unbundled["modules"].items():
            if name in self.modules:
                if module["content"] != self.modules[name]:
                    raise Exception(f"Inconsistent module {name}.")
            else:
                self.modules[name] = module["content"]
                self.module_dir.joinpath(f"{name}.lua").write_text(
                    module["content"], encoding="utf-8"
                )
        return root_module["content"]
