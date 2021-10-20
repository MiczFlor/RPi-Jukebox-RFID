RPC Command Reference
***********************


This file provides a summary of all the callable functions through the RPC. It depends on the loaded modules

.. contents::

Module: publishing
-------------------------------------------


**loaded_from**:    components.publishing

Plugin interface for Jukebox Publisher


.. py:function:: publishing.republish(topic=None)
    :noindex:

    Re-publish the topic tree 'topic' to all subscribers
    
    :param topic: Topic tree to republish. None = resend all


Module: volume
-------------------------------------------


**loaded_from**:    components.volume

Volume Control Factory for run-time switching of volume control plugin


.. py:function:: volume.factory.get_active()
    :noindex:

    


.. py:function:: volume.factory.list()
    :noindex:

    List the available volume services


.. py:function:: volume.factory.set_active(key)
    :noindex:

    Set the active volume service which gets registered as 'ctrl'


.. py:function:: volume.ctrl.dec_volume(step=3)
    :noindex:

    


.. py:function:: volume.ctrl.get_volume()
    :noindex:

    


.. py:function:: volume.ctrl.inc_volume(step=3)
    :noindex:

    


.. py:function:: volume.ctrl.mute(mute_on=True)
    :noindex:

    


.. py:function:: volume.ctrl.set_volume(volume)
    :noindex:

    


.. py:function:: volume.ctrl.unmute()
    :noindex:

    


Module: jingle
-------------------------------------------


**loaded_from**:    components.jingle

Jingle Playback Factory for extensible run-time support of various file types


.. py:function:: jingle.play(filename)
    :noindex:

    Play the jingle using the configured jingle service
    
    Note: This runs in a separate thread. And this may cause troubles
    when changing the volume ctrl interface and volume level before
    and after the sound playback: There is nothing to prevent another
    thread from changing the active factory while playback happens
    and afterwards we change it back to where it was before!
    
    There is no way around this dilemma except for not running the jingle as a
    separate thread. Currently (as thread) even the RPC is started before the sound
    is finished and the volume is reset to normal...
    
    However: Volume plugin is loaded before jingle and sets the default
    volume. No interference here. It can now only happen
    if (a) through the RPC or (b) some other plugin the volume is changed. Okay, now
    (a) let's hope that there is enough delay in the user requesting a volume change
    (b) let's hope no other plugin wants to do that
    and take our changes with the threaded approach.
    
    Also note that the MPD plugin starts while the jingle is still playing and starts polling and publishing
    the volume through the current volume service immediately. But in a way that is correct, as this reflects
    the current volume before going back to startup volume


.. py:function:: jingle.play_startup()
    :noindex:

    Play the startup sound (using jingle.play)


.. py:function:: jingle.play_shutdown()
    :noindex:

    Play the shutdown sound (using jingle.play)


Module: player
-------------------------------------------


**loaded_from**:    components.playermpd

Package for interfacing with the MPD Music Player Daemon


.. py:function:: player.ctrl.get_current_song(param)
    :noindex:

    


.. py:function:: player.ctrl.get_player_type_and_version()
    :noindex:

    


.. py:function:: player.ctrl.list_albums()
    :noindex:

    


.. py:function:: player.ctrl.list_all_dirs()
    :noindex:

    


.. py:function:: player.ctrl.map_filename_to_playlist_pos(filename)
    :noindex:

    


.. py:function:: player.ctrl.move()
    :noindex:

    


.. py:function:: player.ctrl.next()
    :noindex:

    Play next track in current playlist


.. py:function:: player.ctrl.pause(state: int = 1)
    :noindex:

    Enforce pause to state (1: pause, 0: resume)
    
    This is what you want as card removal action: pause the playback, so it can be resumed when card is placed
    on the reader again. What happens on re-placement depends on configured second swipe option


.. py:function:: player.ctrl.play()
    :noindex:

    


.. py:function:: player.ctrl.play_card(folder: str, recursive: bool = False)
    :noindex:

    Main entry point for trigger music playing from RFID reader. Decodes second swipe options before playing folder content
    
    Checks for second (or multiple) trigger of the same folder and calls first swipe / second swipe action
    accordingly.
    
    :param folder: Folder path relative to music library path
    :param recursive: Add folder recursively


.. py:function:: player.ctrl.play_folder(folder: str, recursive: bool = False) -> None
    :noindex:

    Playback a music folder.
    
    Folder content is added to the playlist as described by :mod:`jukebox.playlistgenerator`.
    The playlist is cleared first.
    
    :param folder: Folder path relative to music library path
    :param recursive: Add folder recursively


.. py:function:: player.ctrl.playerstatus()
    :noindex:

    


.. py:function:: player.ctrl.playlistaddplay(folder: str, recursive: bool = False) -> None
    :noindex:

    


.. py:function:: player.ctrl.playlistinfo()
    :noindex:

    


.. py:function:: player.ctrl.playsingle()
    :noindex:

    


.. py:function:: player.ctrl.prev()
    :noindex:

    


.. py:function:: player.ctrl.queue_load(folder)
    :noindex:

    


.. py:function:: player.ctrl.remove()
    :noindex:

    


.. py:function:: player.ctrl.repeatmode(mode)
    :noindex:

    


.. py:function:: player.ctrl.replay()
    :noindex:

    Re-start playing the last-played folder
    
    Will reset settings to folder config


.. py:function:: player.ctrl.replay_if_stopped()
    :noindex:

    Re-start playing the last-played folder unless playlist is still playing
    
    .. note:: To me this seems much like the behaviour of play,
        but we keep it as it is specifically implemented in box 2.X


.. py:function:: player.ctrl.resume()
    :noindex:

    


.. py:function:: player.ctrl.rewind()
    :noindex:

    Re-start current playlist from first track
    
    Note: Will not re-read folder config, but leave settings untouched


.. py:function:: player.ctrl.seek(new_time)
    :noindex:

    


.. py:function:: player.ctrl.shuffle(random)
    :noindex:

    There is a bit of a name mix up here


.. py:function:: player.ctrl.stop()
    :noindex:

    


.. py:function:: player.ctrl.toggle()
    :noindex:

    Toggle pause state, i.e. do a pause / resume depending on current state


.. py:function:: player.ctrl.update()
    :noindex:

    


Module: cards
-------------------------------------------


**loaded_from**:    components.rfid.cards

Handling the RFID card database


.. py:function:: cards.list_cards()
    :noindex:

    Provide a summarized, decoded list of all card actions
    
    This is intended as basis for a formatter function
    
    Format: 'id': {decoded_function_call, ignore_same_id_delay, ignore_card_removal_action, description, from_alias}


.. py:function:: cards.delete_card(card_id: str, auto_save: bool = True)
    :noindex:

    :param auto_save:
    :param card_id:


.. py:function:: cards.register_card(card_id: str, cmd_alias: str, args: Union[List, NoneType] = None, kwargs: Union[Dict, NoneType] = None, ignore_card_removal_action: Union[bool, NoneType] = None, ignore_same_id_delay: Union[bool, NoneType] = None, overwrite: bool = False, auto_save: bool = True)
    :noindex:

    Register a new card based on quick-selection
    
    If you are going to call this through the RPC it will get a little verbose
    
    **Example:** Registering a new card with ID *0009* for increment volume with a custom argument to inc_volume
    (*here: 15*) and custom *ignore_same_id_delay value*::
    
        plugin.call_ignore_errors('cards', 'register_card',
                                  args=['0009', 'inc_volume'],
                                  kwargs={'args': [15], 'ignore_same_id_delay': True, 'overwrite': True})


.. py:function:: cards.register_card_custom()
    :noindex:

    Register a new card with full RPC call specification (Not implemented yet)


.. py:function:: cards.load_card_database(filename)
    :noindex:

    


.. py:function:: cards.save_card_database(filename=None, *, only_if_changed=True)
    :noindex:

    Store the current card database. If filename is None, it is saved back to the file it was loaded from


Module: rfid
-------------------------------------------


**loaded_from**:    components.rfid.reader




Module: timers
-------------------------------------------


**loaded_from**:    components.timers




.. py:function:: timers.timer_shutdown.cancel()
    :noindex:

    Cancel the timer


.. py:function:: timers.timer_shutdown.get_timeout()
    :noindex:

    Get the configured time-out
    
    :return: The total wait time. (Not the remaining wait time!)


.. py:function:: timers.timer_shutdown.is_alive()
    :noindex:

    Check if timer is active


.. py:function:: timers.timer_shutdown.publish()
    :noindex:

    Publish the current state and config


.. py:function:: timers.timer_shutdown.set_timeout(wait_seconds: float)
    :noindex:

    Set a new time-out in seconds. Re-starts the timer if already running!


.. py:function:: timers.timer_shutdown.start(wait_seconds=None)
    :noindex:

    Start the timer (with default or new parameters)


.. py:function:: timers.timer_shutdown.trigger()
    :noindex:

    Trigger the next target execution before the time is up


.. py:function:: timers.timer_stop_player.cancel()
    :noindex:

    Cancel the timer


.. py:function:: timers.timer_stop_player.get_timeout()
    :noindex:

    Get the configured time-out
    
    :return: The total wait time. (Not the remaining wait time!)


.. py:function:: timers.timer_stop_player.is_alive()
    :noindex:

    Check if timer is active


.. py:function:: timers.timer_stop_player.publish()
    :noindex:

    Publish the current state and config


.. py:function:: timers.timer_stop_player.set_timeout(wait_seconds: float)
    :noindex:

    Set a new time-out in seconds. Re-starts the timer if already running!


.. py:function:: timers.timer_stop_player.start(wait_seconds=None)
    :noindex:

    Start the timer (with default or new parameters)


.. py:function:: timers.timer_stop_player.trigger()
    :noindex:

    Trigger the next target execution before the time is up


.. py:function:: timers.timer_fade_volume.cancel()
    :noindex:

    Cancel the timer


.. py:function:: timers.timer_fade_volume.get_timeout()
    :noindex:

    Get the configured time-out
    
    :return: The total wait time. (Not the remaining wait time!)


.. py:function:: timers.timer_fade_volume.is_alive()
    :noindex:

    Check if timer is active


.. py:function:: timers.timer_fade_volume.publish()
    :noindex:

    Publish the current state and config


.. py:function:: timers.timer_fade_volume.set_timeout(wait_seconds: float)
    :noindex:

    Set a new time-out in seconds. Re-starts the timer if already running!


.. py:function:: timers.timer_fade_volume.start(iterations=None, wait_seconds_per_iteration=None)
    :noindex:

    Start the timer (with default or new parameters)


.. py:function:: timers.timer_fade_volume.trigger()
    :noindex:

    Trigger the next target execution before the time is up


Module: host
-------------------------------------------


**loaded_from**:    components.hostif.linux




.. py:function:: host.shutdown()
    :noindex:

    Shutdown the host machine


.. py:function:: host.reboot()
    :noindex:

    Reboot the host machine


.. py:function:: host.jukebox_is_service()
    :noindex:

    Check if current Jukebox process is running as a service


.. py:function:: host.restart_service()
    :noindex:

    Restart Jukebox App if running as a service


.. py:function:: host.get_disk_usage(path='/')
    :noindex:

    Return the disk usage in Megabytes as dictionary for RPC export


.. py:function:: host.get_cpu_temperature()
    :noindex:

    Get the CPU temperature with single decimal point
    
    No error handling: this is expected to take place up-level!


.. py:function:: host.publish_cpu_temperature()
    :noindex:

    


.. py:function:: host.wlan_disable_power_down(card=None)
    :noindex:

    Turn off power management of wlan. Keep RPi reachable via WLAN
    
    This must be done after every reboot
    card=None takes card from configuration file


.. py:function:: host.timer_temperature.cancel()
    :noindex:

    Cancel the timer


.. py:function:: host.timer_temperature.get_timeout()
    :noindex:

    Get the configured time-out
    
    :return: The total wait time. (Not the remaining wait time!)


.. py:function:: host.timer_temperature.is_alive()
    :noindex:

    Check if timer is active


.. py:function:: host.timer_temperature.publish()
    :noindex:

    Publish the current state and config


.. py:function:: host.timer_temperature.set_timeout(wait_seconds: float)
    :noindex:

    Set a new time-out in seconds. Re-starts the timer if already running!


.. py:function:: host.timer_temperature.start(wait_seconds=None)
    :noindex:

    Start the timer (with default or new parameters)


.. py:function:: host.timer_temperature.trigger()
    :noindex:

    Trigger the next target execution before the time is up


Module: alsaif
-------------------------------------------


**loaded_from**:    components.alsaif

ALSA Volume Control Plugin Package for volume.VolumeFactory


Module: alsaif.alsawave
-------------------------------------------


**loaded_from**:    components.alsaif.alsawave

ALSA wave jingle Service for jingle.JingleFactory


.. py:function:: alsaif.alsawave.alsawave.play(filename)
    :noindex:

    Play the wave file


Module: jingle.jinglemp3
-------------------------------------------


**loaded_from**:    components.jingle.jinglemp3

Generic MP3 jingle Service for jingle.JingleFactory


.. py:function:: jingle.jinglemp3.jinglemp3.play(filename)
    :noindex:

    Play the MP3 file


Module: music_cover_art
-------------------------------------------


**loaded_from**:    components.music_cover_art

Read all cover art from music save it to a cache for the UI to load


.. py:function:: music_cover_art.ctrl.get_by_filename_as_base64(audio_src: str)
    :noindex:

    


Module: misc
-------------------------------------------


**loaded_from**:    components.misc

Miscellaneous function package


.. py:function:: misc.rpc_cmd_help()
    :noindex:

    Return all commands for RPC


.. py:function:: misc.get_all_loaded_packages()
    :noindex:

    Get all successfully loaded plugins


.. py:function:: misc.get_all_failed_packages()
    :noindex:

    Get all plugins with error during load or initialization


.. py:function:: misc.get_start_time()
    :noindex:

    Time when JukeBox has been started


.. py:function:: misc.get_log_debug()
    :noindex:

    Get the log file (from the debug_file_handler)


.. py:function:: misc.get_log_error()
    :noindex:

    Get the log file (from the error_file_handler)


.. py:function:: misc.get_version()
    :noindex:

    


.. py:function:: misc.get_git_state()
    :noindex:

    Return git state information for the current branch




Generation notes
-------------------------------------------


This is an automatically generated file from the loaded plugins:

* *publishing*: components.publishing
* *volume*: components.volume
* *jingle*: components.jingle
* *player*: components.playermpd
* *cards*: components.rfid.cards
* *rfid*: components.rfid.reader
* *timers*: components.timers
* *host*: components.hostif.linux
* *alsaif*: components.alsaif
* *alsaif.alsawave*: components.alsaif.alsawave
* *jingle.jinglemp3*: components.jingle.jinglemp3
* *music_cover_art*: components.music_cover_art
* *misc*: components.misc
