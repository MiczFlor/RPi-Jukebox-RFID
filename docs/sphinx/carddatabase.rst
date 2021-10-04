Card Database
*****************

In the card database an action is assigned to every card. This action is triggered on every swipe of the card.

.. important:: Card IDs **must** be strings! So, be sure to quote numbers!

Actions
-------------------------

This is the function to be called every time when the card is swiped (or placed) on the reader. In principle every
RPC-callable function can be called. There are pre-defined 'quick-selections' for commonly used functions.
Take a look at the file ``shared/settings/card_actions_reference.txt`` to get an overview of available quick select options.
It's an auto-generated file, that gets written after first start of the Jukebox.

Here are some examples for card is '0001' to '0003' using quick select options:

.. code-block:: yaml

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

.. note::
    * Remember card ids must be strings! So, quote them!
    * *args* must be a **list** of arguments to be passed! Even if ony a single argument is passed. So, use *args: [value]*.
      We try catch mis-uses but that might not always work.

Additional options
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

ignore_card_removal_action: true | false
    Only applies when using a place-capable reader and *place_not_swipe* is *true*. This option is ignored otherwise,
    so it does not hurt.

    Do not execute card removal action, when this card is removed from the reader.  Useful for command card,
    that e.g. enable the shutdown timer

    .. code-block:: yaml

        '0004':
            quick_select: timer_shutdown
            ignore_card_removal_action: true


ignore_same_id_delay: true | false
    Override the same_id_delay parameter for this card. If true, the same_id_delay for this card is treated as 0.
    This makes sense e.g. for an "increase volume" card in combination with a place-capable RFID reader.
    As long as the card is placed on the reader, the volume is increased.

    .. note:: This parameter causes *ignore_card_removal_action* to be treated as true

    .. code-block:: yaml

        '0005':
            quick_select: incr_volume
            ignore_same_id_delay: true
            ignore_card_removal_action: true

Full RPC action specification
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You have seen some examples card actions using the *quick_select* configuration. A full RPC action can also be specified
using the following syntax.

.. code-block:: yaml

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
