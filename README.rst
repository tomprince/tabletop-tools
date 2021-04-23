Tabletop Simulator Mod Tools
----------------------------

This is a collection of tools for working Tabletop Simulatator mods.

To build a mod::

    $ tts repack

This will put the module at ``build/savegame.json``. You can also pass a path for where to build the module.

To unpack a module::

    $ tts unpack <...path/to/savegame.json...>

to unpack a savegame.


Config
......

You can provide a ``tabletop-tools.toml`` at the root of a savegame, to configure tabletop-tools.

Currently, there is one supported option (``quantize``), that causes tabletop-tools to round floats to the nearest 0.0001.

.. code:: toml

   quantize = true
