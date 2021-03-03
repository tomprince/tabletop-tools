=========
Changelog
=========

This is a record of all past tabletop-tools releases and what went into them,
in reverse chronological order. All previous releases should still be available
on `PyPI <https://pypi.org/project/tabletop-tools/>`__.

.. changelog start

v0.5.0
......
Backout luabundler support. It requires having node installed as well as python
which is not great.  I hope to add support for it again, without that dependency,
but back it out for now, for the spirit island mod.


v0.4.0
......
- **BREAKING CHANGE**: Rename ``unpacked-savegame.json`` to ``savegame.json`` and ``global-script.lua`` to ``script.lua``.
- Change default repacked savegame name to ``build/packed-savegame.json``.


v0.3.2
......
More luabundle code refactoring.


v0.3.1
......
Refactor luabundle code.


v0.3.0
......
Add support for running luabundler on input/output.


v0.2.0
......
* Handle running in non-unicode locales.
* Don't escape unicode in generated JSON.


v0.1.0
......
Add support for unpacking from a workshop mod directly.


v0.0.7
......
Handle non-existent script-state and XML UI at the top-level.


v0.0.6
......

Expand `LuaScriptState` and `XmlUI` into individual files in objects.


v0.0.5
......

Add trailing newlines to unpacked json files.


v0.0.4
......

* Add a basic README.
* Update license to the Mozilla Public License 2.0.


v0.0.3
......

* Fix handling of multiple objects with identical GUIDs in containers.
* Stop using windows line endings in generated mod.
* Fix version bump string formatting for black.


v0.0.2
......

* Update project metadata.
* Add release automation.


0.0.1
.....

Initial release.
