RPC Command Alias Reference
***************************


.. |--| unicode:: U+2014
.. |->| unicode:: U+21d2

.. py:function:: play_card(...) -> player.ctrl.play_card(folder: str, recursive: bool = False)
    :noindex:

    **Play music folder triggered by card swipe**

    Main entry point for trigger music playing from RFID reader. Decodes second swipe options before playing folder content
    
    Checks for second (or multiple) trigger of the same folder and calls first swipe / second swipe action
    accordingly.
    
    :param folder: Folder path relative to music library path
    :param recursive: Add folder recursively

    .. note:: This function you'll want to use most often

.. py:function:: pause(...) -> player.ctrl.pause(state: int = 1)
    :noindex:

    Enforce pause to state (1: pause, 0: resume)
    
    This is what you want as card removal action: pause the playback, so it can be resumed when card is placed
    on the reader again. What happens on re-placement depends on configured second swipe option

    .. note:: This is what you want as card removal action for place capable readers

    Default actions modifiers
         **ignore_card_removal_action** |--| True

.. py:function:: set_volume(...) -> volume.ctrl.set_volume(volume)
    :noindex:

    

    Default actions modifiers
         **ignore_card_removal_action** |--| True

.. py:function:: inc_volume(...) -> volume.ctrl.inc_volume(step=3)
    :noindex:

    

    .. note:: For place-capable readers increment volume as long as card is on reader

    Default actions modifiers
         **ignore_card_removal_action** |--| True

         **ignore_same_id_delay** |--| True

.. py:function:: dec_volume(...) -> volume.ctrl.inc_volume(step=3)
    :noindex:

    

    Default actions modifiers
         **ignore_card_removal_action** |--| True

         **ignore_same_id_delay** |--| True

.. py:function:: set_max_volume(...) -> volume.ctrl.set_max_volume(---UNKNOWN---)
    :noindex:

    ERROR: NameError: Plugin object 'volume.ctrl' has not attribute 'set_max_volume'

    Default actions modifiers
         **ignore_card_removal_action** |--| True

.. py:function:: shutdown(...) -> host.shutdown()
    :noindex:

    Shutdown the host machine

    Default actions modifiers
         **ignore_card_removal_action** |--| True

.. py:function:: reboot(...) -> host.reboot()
    :noindex:

    Reboot the host machine

    Default actions modifiers
         **ignore_card_removal_action** |--| True

.. py:function:: shutdown_after(...) -> timers.timer_shutdown.start(wait_seconds=None)
    :noindex:

    **Start the shutdown timer**

    Start the timer (with default or new parameters)

    Default actions modifiers
         **ignore_card_removal_action** |--| True

.. py:function:: fade_volume(...) -> timers.timer_fade_volume.start(iterations=None, wait_seconds_per_iteration=None)
    :noindex:

    **Start the volume fade out timer and shutdown**

    Start the timer (with default or new parameters)

    Default actions modifiers
         **ignore_card_removal_action** |--| True

.. py:function:: stop_after(...) -> timers.timer_stop_player.start(wait_seconds=None)
    :noindex:

    **Start the stop music timer**

    Start the timer (with default or new parameters)

    Default actions modifiers
         **ignore_card_removal_action** |--| True

