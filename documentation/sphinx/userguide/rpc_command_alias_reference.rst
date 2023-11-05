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

.. py:function:: play_album(...) -> player.ctrl.play_album(albumartist: str, album: str)
    :noindex:

    **Play Album triggered by card swipe**

    Playback a album found in MPD database.
    
    All album songs are added to the playlist
    The playlist is cleared first.
    
    :param albumartist: Artist of the Album provided by MPD database
    :param album: Album name provided by MPD database

    .. note:: This function plays the content of a given album

.. py:function:: play_single(...) -> player.ctrl.play_single(song_url)
    :noindex:

    **Play a single song triggered by card swipe**

    

    .. note:: This function plays the content of a given song URL

.. py:function:: play_folder(...) -> player.ctrl.play_folder(folder: str, recursive: bool = False) -> None
    :noindex:

    **Play a folder URL triggered by card swipe**

    Playback a music folder.
    
    Folder content is added to the playlist as described by :mod:`jukebox.playlistgenerator`.
    The playlist is cleared first.
    
    :param folder: Folder path relative to music library path
    :param recursive: Add folder recursively

    .. note:: This function plays the content of a given folder URL

.. py:function:: pause(...) -> player.ctrl.pause(state: int = 1)
    :noindex:

    Enforce pause to state (1: pause, 0: resume)
    
    This is what you want as card removal action: pause the playback, so it can be resumed when card is placed
    on the reader again. What happens on re-placement depends on configured second swipe option

    .. note:: This is what you want as card removal action for place capable readers

    Default actions modifiers
         **ignore_card_removal_action** |--| True

.. py:function:: next_song(...) -> player.ctrl.next()
    :noindex:

    Play next track in current playlist

    Default actions modifiers
         **ignore_card_removal_action** |--| True

.. py:function:: prev_song(...) -> player.ctrl.prev()
    :noindex:

    

    Default actions modifiers
         **ignore_card_removal_action** |--| True

.. py:function:: toggle(...) -> player.ctrl.toggle()
    :noindex:

    Toggle pause state, i.e. do a pause / resume depending on current state

    Default actions modifiers
         **ignore_card_removal_action** |--| True

.. py:function:: set_volume(...) -> volume.ctrl.set_volume(volume: int)
    :noindex:

    Set the volume (0-100) for the currently active output

    Default actions modifiers
         **ignore_card_removal_action** |--| True

.. py:function:: change_volume(...) -> volume.ctrl.change_volume(step: int)
    :noindex:

    Increase/decrease the volume by step for the currently active output

    .. note:: For place-capable readers increment volume as long as card is on reader

    Default actions modifiers
         **ignore_card_removal_action** |--| True

         **ignore_same_id_delay** |--| True

.. py:function:: set_soft_max_volume(...) -> volume.ctrl.set_soft_max_volume(max_volume: int)
    :noindex:

    Limit the maximum volume to max_volume for the currently active output

    Default actions modifiers
         **ignore_card_removal_action** |--| True

.. py:function:: toggle_output(...) -> volume.ctrl.toggle_output()
    :noindex:

    Toggle the audio output sink

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

.. py:function:: say_my_ip(...) -> host.say_my_ip(option='full')
    :noindex:

    

    Default actions modifiers
         **ignore_card_removal_action** |--| True

.. py:function:: timer_shutdown(...) -> timers.timer_shutdown.start(wait_seconds=None)
    :noindex:

    **Start the shutdown timer**

    Start the timer (with default or new parameters)

    Default actions modifiers
         **ignore_card_removal_action** |--| True

.. py:function:: timer_fade_volume(...) -> timers.timer_fade_volume.start(iterations=None, wait_seconds_per_iteration=None)
    :noindex:

    **Start the volume fade out timer and shutdown**

    Start the timer (with default or new parameters)

    Default actions modifiers
         **ignore_card_removal_action** |--| True

.. py:function:: timer_stop_player(...) -> timers.timer_stop_player.start(wait_seconds=None)
    :noindex:

    **Start the stop music timer**

    Start the timer (with default or new parameters)

    Default actions modifiers
         **ignore_card_removal_action** |--| True

