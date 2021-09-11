# RFID Reader

Cards placed on the reader trigger an action. An action may be any callable plugin function through the RPC with any arguments.
Typically, this would be "play some folder", but can also be "activate shutdown timer", or "increase volume". 
This is configured in the [Card Database]. 

You may configure a single or even multiple parallel readers (of different or identical types).

Successive card swipes are suppressed to avoid bouncing effects. This can be deactivated for individual cards.

## Reader Types

TBD

## Reader Configuration 

To configure RFID reader(s), please tun the tool 'src/jukebox/run_register_rfid.py'. 
It will generate the reader configuration file at `shared/settings/rfid.yaml`. 
You can re-run the tool to change the settings any time.

Some options are not covered by the tool. You may change the file manually. 

~~~
rfid:
  readers:
    read_00:
        module: fake_reader_gui
        config: ....
        same_id_delay: float|integer
        log_ignored_cards: true|false
        place_not_swipe:
            enabled: true|false
            card_removal_action:
                quick_selection: none | pause           
~~~

For each reader, there is an entry `read_XX`.

**module** and **config**:

These are filled by the RFID configuration tool. 
After running the tool, you may manually change some settings here, as not everything can
be configured through the tool. Note, that re-running the tool will completely rewrite this configuration file.


**same_id_delay**: float | integer

Minimum delay in seconds between two card detections before triggering a new action. This 
is to prevent double triggering or bouncing.

**place_not_swipe**: true | false

For place-capable RFID readers enable dual action mode: 
a start action (e.g. playing) on card placement and card removal action (e.g. pause).

**card_removal_action**: Dictionary

Action on card removal. Only relevant if place_not_swipe is true. The action is identical for all cards read on 
that reader. The removal-action can be set to ignore on a card-by-card basis. More on card action configurations in [Actions]

Developer's note: The reason for a unique removal action for all cards is that card triggering and card removal are happening 
in two separate threads. Removal needs to be in a time-out thread. Thus, we would need to transport information  from
one thread to another. Of course, can be done, but is not implemented (yet). Ignoring card removal is much easier and is implemented.

**log_ignored_cards**: true | false
Log all card that are ignored due to same_id_delay. This is a developer's option. Don't use unless debugging as it has
the potential to spam your log files.

## Second Swipe
Looking for 'Second Swipe' option? That is part of the Player configuration and not part of the RFID configuration, as 
the 'Second Swipe' action needs to take into account the player state, which can also be altered through the WebUI

## Card Database

In the card database an action is assigned to every card. This is triggered on every swipe of the card.

Card IDs **must** be strings! So, be sure to quote numbers!

### Actions

This is the function to be called every time when the card is swiped (or placed) on the reader. In principle every
RPC-callable function can be called. There are pre-defined 'quick-selections' for commonly used functions. 
Take a look at the file `shared/settings/card_actions_reference.txt` to get an overview of available quick select options. 
It's an auto-generated file, that gets written after first start of the Jukebox. 

Here are some examples for card is '0001' to '0003' using quick select options:
~~~
'0001':
    # A function without any arguments 
    # Here: pause playback
    quick_select: pause
'0002':
    # A pre-defined function with arguments
    # Here: Trigger music playback through the card interface 
    quick_select: play_card
    args: [path/to/folder]
'0003':
    # A pre-defined function with keyword arguments. Args and kwargs can also be mixed. 
    # Args and Kwargs translate directly into the function python call
    # Some as in '0002' but using kwargs 
    quick_select: play_card
    kwargs: 
        folder: path/to/folder
~~~

#### Some noteworthy things:

- Remember card ids must be strings! Soe, quote them
- args must a **list** of arguments to be passed! Even if ony a single argument is passed. So, use `args: [value]`. 
  We try catch mis-uses but that might not always work.

#### Additional options:

**ignore_card_removal_action**: true | false

Only applies when using a place-capable reader and `place_not_swipe` is `true`. This option is ignored otherwise, 
so it does not hurt.

Do not execute card removal action, when this card is removed from the reader.  Useful for command card, 
that e.g. enable the shutdown timer

~~~
'0004':
    quick_select: timer_shutdown
    ignore_card_removal_action: true
~~~


**ignore_same_id_delay**: true | false

Override the same_id_delay parameter for this card. If true, the same_id_delay for this card is treated as 0. 
This makes sense e.g. for an "increase volume" card in combination with a place-capable RFID reader. 
As long as the card is placed on the reader, the volume is increased. 

*Note*: This parameter causes 'ignore_card_removal_action' to be treated as true

~~~
'0005':
    quick_select: incr_volume
    ignore_same_id_delay: true
    ignore_card_removal_action: true
~~~

#### Full RPC action specification:

You have seen some examples card actions using the `quick_select` configuration. A full RPC action can also be specified
using the following syntax.

~~~
'0006':
    # Option 1: Don't specify 'quick_select'
    # Here: Set the volume to level 12   
    package: volume
    plugin: ctrl
    method: set_volume
    args: [12]
'0007':
    # Option 2: Set 'quick_select' to custom
    # Here: Set the volume to level 12   
    quick_select: custom
    package: volume
    plugin: ctrl
    method: set_volume
    args: [12]
~~~
