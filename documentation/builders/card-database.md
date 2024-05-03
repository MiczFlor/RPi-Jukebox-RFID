# Card Database

In the card database, an RPC command is assigned to every card.

This RPC command is called every time when the card is swiped (or
placed) on the reader. Every RPC callable function can be called. See
[RPC Commands](rpc-commands.md) for an introduction.

The card database is stored in `shared\settings\cards.yaml`. Here are
some examples for RPC command assignments to cards \'0001\' to \'0003\'
using the alias option:

> [!IMPORTANT]
> Card IDs **must** be strings! So, be sure to quote numbers!

``` yaml
'0001':
    # A RPC command using the alias definition without any arguments
    # Here: pause playback
    alias: pause
'0002':
    # A RPC command using the alias definition with one arguments
    # Here: Trigger music playback through the card interface
    alias: play_card
    args: [path/to/folder]
'0003':
    # A RPC command using keyword arguments. Args and kwargs can also be mixed.
    # Args and Kwargs translate directly into the function python call
    # Some as in '0002' but using kwargs
    alias: play_card
    kwargs:
        folder: path/to/folder
```

> [!NOTE]
>
> * Remember card ids must be strings! So, quote them!
> * *args* must be
a **list** of arguments to be passed! Even if ony a single argument is
passed. So, use *args: \[value\]*. We try catch mis-uses but that might
not always work.

## Additional options

In addition to the RPC commands, these options may be specified for
every card

### ignore_card_removal_action: true \| false (default: false)

Only applies when using a place-capable reader and *place_not_swipe* is *true*. This option is ignored otherwise, so it does not hurt.

Do not execute card removal action, when this card is removed from
the reader. Useful for command card, that e.g. enable the shutdown
timer

``` yaml
'0004':
    alias: timer_shutdown
    ignore_card_removal_action: true
```

### ignore_same_id_delay: true \| false (default: false)

Override the `same_id_delay` parameter from the reader configuration
for this card. If true, the `same_id_delay` for this card is treated
as 0. This makes sense e.g., for an \"increase volume\" card in
combination with a place-capable RFID reader. As long as the card is
placed on the reader, the volume is increased.

> [!NOTE]
> This parameter causes *ignore_card_removal_action* to be treated as true

``` yaml
'0005':
    alias: incr_volume
    ignore_same_id_delay: true
    ignore_card_removal_action: true
```

## Full RPC action specification

You have seen some examples card actions using the *alias*
configuration. A full RPC action can also be specified using the
following syntax:

``` yaml
'0006':
    # Option 1: Omit the keyword 'alias'
    # Here: Set the volume to level 12
    package: volume
    plugin: ctrl
    method: set_volume
    args: [12]
'0007':
    # Option 2: Set 'alias' to custom
    # Here: Set the volume to level 12
    alias: custom
    package: volume
    plugin: ctrl
    method: set_volume
    args: [12]
```
