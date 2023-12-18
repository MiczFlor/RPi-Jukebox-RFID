# RFID

## Basics

Cards placed on the reader trigger an action. An action may be any
callable plugin function through the RPC with any arguments. Typically,
this would be "play some folder", but can also be "activate shutdown
timer", or "increase volume". This is configured in the
[Card Database](../../builders/card-database.md).

You may configure a single or even multiple parallel readers (of
different or identical types).

Successive card swipes are suppressed to avoid bouncing effects. This
behavior can be deactivated for individual cards.

## Reader Types

#### place-capable:

Some readers give a single event signal when the card is placed on
the reader. This is sufficient to build a fully-featured Jukebox.
Other readers give a continuous signal. They allow both card
placements and card removals. This can be used to play the Jukebox
when a card is placed and to pause it when it's removed.

Generally, **not** all [USB-based RFID readers](genericusb.md) are place-capable.

The known place-capable readers are [RDM6300 Reader](rdm6300.md), [MFRC522 SPI Reader](mfrc522_spi.md) or [PN532 I2C Reader](pn532_i2c.md).

#### Frequency:

Readers operate on one of two different frequencies: 125kHz or 13.56 MHz. Make sure to buy compatible cards, RFID stickers or key fobs working with the same frequency as the reader.

## Reader Configuration

During the installation process, you can already configure a RFID
reader. To manually configure RFID reader(s) run the [RFID reader configuration tool](../coreapps.md#RFID-Reader).

It will generate a reader configuration file at
`shared/settings/rfid.yaml`. You can re-run the tool to change the
settings any time.

Some options are not covered by the tool. You may change the file
manually.

``` yaml
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
                alias: pause
```

For each reader, there is an entry `read_XX`.

#### module:

Indicates the Python package used for this reader. Filled by the RFID configuration tool.

#### config:

Filled by the [RFID reader configuration tool](../coreapps.md#RFID-Reader) based on default values and user input. After running the tool, you may manually change some settings here, as not everything can be configured through the tool. Note that re-running the tool will completely rewrite the configuration file.

#### same_id_delay: float \| integer

Minimum delay in seconds between 2 card detections before triggering a new action. This is to prevent double triggering or bouncing.

#### place_not_swipe: true \| false

For place-capable RFID readers enable dual action mode: a start action (e.g. playing) on card placement and card removal action (e.g. pause).

#### card_removal_action: Dictionary

Executes the given function on card removal. Only relevant if place_not_swipe is true. The action is identical for all cards read on that reader. The removal-action can be set to ignored on a card-by-card basis. More on card action configurations in [RPC Commands](../../builders/rpc-commands.md).

> [!NOTE]
> Developer's note: The reason for a unique removal action for all cards is that card triggering and card removal are happening in two separate threads. Removal needs to be in a time-out thread. Thus, we would need to transport information from one thread to another. This can be done of course but is not implemented (yet). Ignoring card removal is much easier and works for now.

#### log_ignored_cards: true \| false

Log all cards that are ignored due to same_id_delay. This is a option for developers. Don't use it unless you need it for debugging as it has the potential to spam your log files.

#### Second Swipe

Looking for 'Second Swipe' option? That is part of the Player configuration and not part of the RFID configuration, as the 'Second Swipe' action needs to take into account the player state, which can also be altered through the WebUI.
