RFID Reader
*****************

Cards placed on the reader trigger an action. An action may be any callable plugin function through the RPC with any arguments.
Typically, this would be "play some folder", but can also be "activate shutdown timer", or "increase volume".
This is configured in the :ref:`carddatabase:Card Database`.

You may configure a single or even multiple parallel readers (of different or identical types).

Successive card swipes are suppressed to avoid bouncing effects. This can be deactivated for individual cards.

.. contents::

Reader Types
------------

place-capable:
    Some readers give a single event signal when the card is placed on the reader. This is amply sufficient
    to build a fully-featured Jukebox. Other readers give a continuous
    signal. The latter allows to also detect card removal and not only card placement. This can be used to
    invoke pause when the card is removed.

    Generally, all :ref:`USB-based RFID readers <rfidreaders:Generic USB reader>` are **not** place-capable.

    The known place-capable readers are :ref:`RDM6300 <rfidreaders:RDM6300 serial UART>`, MFRC522, and PN532.

Reader Configuration
-----------------------

To configure RFID reader(s), :ref:`please run the tool <coreapps:run_register_rfid_reader.py>` ``src/jukebox/run_register_rfid_reader.py``.

It will generate the reader configuration file at ``shared/settings/rfid.yaml``.
You can re-run the tool to change the settings any time. The procedure as for :ref:`coreapps:Configuration` changes applies.

Some options are not covered by the tool. You may change the file manually.

.. code-block:: yaml

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

For each reader, there is an entry ``read_XX``.

module:
    Inidcated the Python package used for this reader. Filled by the RFID configuration tool.

config:
    Filled by the RFID configuration tool basd on default values and user input.
    After running the tool, you may manually change some settings here, as not everything can
    be configured through the tool. Note, that re-running the tool will completely rewrite this configuration file.

same_id_delay: float | integer
    Minimum delay in seconds between two card detections before triggering a new action. This
    is to prevent double triggering or bouncing.

place_not_swipe: true | false
    For place-capable RFID readers enable dual action mode:
    a start action (e.g. playing) on card placement and card removal action (e.g. pause).

card_removal_action: Dictionary
    Action on card removal. Only relevant if place_not_swipe is true. The action is identical for all cards read on
    that reader. The removal-action can be set to ignore on a card-by-card basis. More on card action configurations in [Actions]

    Developer's note: The reason for a unique removal action for all cards is that card triggering and card removal are happening
    in two separate threads. Removal needs to be in a time-out thread. Thus, we would need to transport information  from
    one thread to another. Of course, can be done, but is not implemented (yet). Ignoring card removal is much easier and is implemented.

log_ignored_cards: true | false
    Log all card that are ignored due to same_id_delay. This is a developer's option. Don't use unless debugging as it has
    the potential to spam your log files.

Second Swipe
    Looking for 'Second Swipe' option? That is part of the Player configuration and not part of the RFID configuration, as
    the 'Second Swipe' action needs to take into account the player state, which can also be altered through the WebUI


Supported RFID reader modules
-------------------------------------

Generic USB reader
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: components.rfid.generic_usb.generic_usb


RDM6300 serial UART
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: components.rfid.rdm6300_serial.rdm6300_serial


Mock RFID Reader
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: components.rfid.fake_reader_gui.fake_reader_gui
