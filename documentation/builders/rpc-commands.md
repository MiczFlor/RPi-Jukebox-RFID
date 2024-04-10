# RPC Commands

We use the RPC commands when triggering actions from different inputs like a card swipe,
a GPIO button press, etc. Triggering an action is equal to sending an RPC function call.
In many places the command to send when an input is triggered is configurable in a YAML-file.

## Basics

Consequently, you need to know how to specify the RPC command in the YAML file.
Here is the essence of what you need to know:

An RPC command consists of up to three parts

1. the function to execute (e.g. play_folder, change_volume)
2. the positional arguments (optional)
3. the keyword arguments (optional)

The function specification consists of two (e.g., ``host.shutdown``) or three terms (e.g., ``volume.ctrl.change_volume``).
In configuration files, this will look like this:

```yml
package: host
plugin: shutdown
```

Or like this for a three part function with the argument set to ``5``:

```yml
package: volume
plugin: ctrl
method: change_volume
args: [5]
```

The keyword ``method`` is optional. If needs to be used depends on the function you want to call.

## Aliases

Not so complicated, right? It will get even easier. For common commands we have defined aliases. An alias simply maps
to a pre-defined RPC command, e.g. ``play_folder`` maps to ``player.ctrl.play_folder``.

Instead of

```yml
package: player
plugin: ctrl
method: play_folder
args: [path/to/folder]
```

you can simply specify instead:

```yml
alias: play_folder
args: [path/to/folder]
```

Using in alias is optional. But if the keyword is present in the configuration it takes precedence over an explicit specified RPC command.

## Arguments

Arguments can be specified in similar fashion to Python function arguments: as positional arguments and / or
keyword arguments. Let's check out play_folder, which is defined as:

```python
play_folder(...) -> player.ctrl.play_folder(folder: str, recursive: bool = False)
    :noindex:

    :param folder: Folder path relative to music library path
    :param recursive: Add folder recursively
```

This means it takes two arguments:

* folder of type string
* recursive of type bool

In the following examples, we will always use the alias for smaller configuration text. All three examples
do exactly the same, but use different ways of specifying the command.

```yml
alias: play_folder
args: [path/to/folder, True]
```

```yml
alias: play_folder
args: [path/to/folder]
kwargs:
    recursive: True
```

```yml
alias: play_folder
kwargs:
    folder: path/to/folder
    recursive: True
```

> [!IMPORTANT]
> *args* must be a **list** of arguments to be passed! Even if only a single argument is passed.
> So, use *args: [value]*. We try catch mis-uses but that might not always work.

You will find some more examples the configuration of the [Card Database](card-database.md)

## For developers

To send RPC commands for testing and debugging purpose you can use the [CLI Tool](../developers/coreapps.md#RPC).
Also here is a ready-to-use decoding functions which decodes an RPC command (with or without alias)
from a YAML entry:func:`jukebox.utils.decode_rpc_command`.
