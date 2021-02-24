from pathlib import Path
from typing import Any, Dict, cast

from node_vm2 import NodeVM, VMServer


class Bundler:
    def __init__(self, module_dir: Path) -> None:
        self.module_dir = module_dir
        self.modules: Dict[str, Any] = {}
        self._server: VMServer = VMServer()
        self._server.start()
        self._vm: NodeVM = NodeVM(self._server)
        self._vm.create()
        self._module = self._vm.run(
            Path(__file__).with_name("luabundle.js").read_text()
        )
        if self.module_dir.exists():
            for module in self.module_dir.iterdir():
                if module.is_file() and module.suffix == ".lua":
                    self._module.call_member(
                        "writeFile", module.name, module.read_text(encoding="utf-8")
                    )

    def __del__(self) -> None:
        self._vm.destroy()
        self._server.close()

    def unbundle(self, lua_script: str) -> str:
        if not lua_script.startswith("-- Bundled by luabundle "):
            return lua_script
        unbundled = self._module.call_member("unbundleString", lua_script)
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
        return cast(str, root_module["content"])

    def bundle(self, lua_script: str) -> str:
        return cast(
            str,
            self._module.call_member(
                "bundleString",
                lua_script,
                {
                    "luaVersion": "5.2",
                    "isolate": True,
                    "paths": ["?.lua"],
                    "metadata": True,
                },
            ),
        )
