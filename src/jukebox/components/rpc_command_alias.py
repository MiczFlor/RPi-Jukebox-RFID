"""
This file provides definitions for RPC command aliases

See :ref:`userguide/rpc_commands`
"""

# --------------------------------------------------------------
# Pre-defined aliases
# These aliases can be used by all modules
# Module-specific behaviour modifiers can be simply appended
# Use the functions utils.decode_rpc_command to decode the entries!
# --------------------------------------------------------------
cmd_alias_definitions = {
    # Player
    'play_card': {
        'title': 'Play music folder triggered by card swipe',
        'note': "This function you'll want to use most often",
        'package': 'player',
        'plugin': 'ctrl',
        'method': 'play_card'},
    'pause': {
        'package': 'player',
        'plugin': 'ctrl',
        'method': 'pause',
        'note': "This is what you want as card removal action for place capable readers",
        'ignore_card_removal_action': True},
    # VOLUME
    'set_volume': {
        'package': 'volume',
        'plugin': 'ctrl',
        'method': 'set_volume',
        'ignore_card_removal_action': True},
    'inc_volume': {
        'note': "For place-capable readers increment volume as long as card is on reader",
        'package': 'volume',
        'plugin': 'ctrl',
        'method': 'inc_volume',
        'ignore_card_removal_action': True,
        'ignore_same_id_delay': True},
    'dec_volume': {
        'package': 'volume',
        'plugin': 'ctrl',
        'method': 'inc_volume',
        'ignore_card_removal_action': True,
        'ignore_same_id_delay': True},
    'set_max_volume': {
        'package': 'volume',
        'plugin': 'ctrl',
        'method': 'set_max_volume',
        'ignore_card_removal_action': True},
    # HOST
    'shutdown': {
        'package': 'host',
        'plugin': 'shutdown',
        'ignore_card_removal_action': True},
    'reboot': {
        'package': 'host',
        'plugin': 'reboot',
        'ignore_card_removal_action': True},
    # TIMER
    'shutdown_after': {
        'package': 'timers',
        'plugin': 'timer_shutdown',
        'method': 'start',
        'title': 'Start the shutdown timer',
        'ignore_card_removal_action': True},
    'fade_volume': {
        'package': 'timers',
        'plugin': 'timer_fade_volume',
        'method': 'start',
        'title': 'Start the volume fade out timer and shutdown',
        'ignore_card_removal_action': True},
    'stop_after': {
        'package': 'timers',
        'plugin': 'timer_stop_player',
        'method': 'start',
        'title': 'Start the stop music timer',
        'ignore_card_removal_action': True},
}

# TODO: Transfer RFID command from v2.3...

#
# ### Stop player
# CMDSTOP="%CMDSTOP%"
# ### Mute player
# CMDMUTE="%CMDMUTE%"
# ### Skip next track
# CMDNEXT="%CMDNEXT%"
# ### Skip previous track
# CMDPREV="%CMDPREV%"
# ### Restart the playlist
# CMDREWIND="%CMDREWIND%"
# ### Seek ahead 15 sec.
# CMDSEEKFORW="%CMDSEEKFORW%"
# ### Seek back 15 sec.
# CMDSEEKBACK="%CMDSEEKBACK%"
# ### Pause player
# CMDPAUSE="%CMDPAUSE%"
# ### Resume audio playout
# CMDPLAY="%CMDPLAY%"
# ### Toggle between speakers and bluetooth headphones
# CMDBLUETOOTHTOGGLE="%CMDBLUETOOTHTOGGLE%"
#
# CMDSHUFFLE="%CMDSHUFFLE%" --> Attention shuffle vs random is mixedup
#
#
#
#
# ## Wifi: switch on/off and other
# ### Enable Wifi
# ENABLEWIFI="%ENABLEWIFI%"
# ### Disable Wifi
# DISABLEWIFI="%DISABLEWIFI%"
# ### Toggle Wifi on/off
# TOGGLEWIFI="%TOGGLEWIFI%"
# ### Read out the Wifi IP over the Phoniebox speakers
# CMDREADWIFIIP="%CMDREADWIFIIP%"
#
# ## Recording audio commands
# ### Start recording for 10 sec. duration
# RECORDSTART10="%RECORDSTART10%"
# ### Start recording for 60 sec. duration
# RECORDSTART60="%RECORDSTART60%"
# ### Start recording for 600 sec. duration
# RECORDSTART600="%RECORDSTART600%"
# ### Stop recording
# RECORDSTOP="%RECORDSTOP%"
# ### Replay latest recording
# RECORDPLAYBACKLATEST="%RECORDPLAYBACKLATEST%"
#
#
# ### Switch between primary/secondary audio iFace --> this seems highly dodgy. Only changes iFace in global config, not mpd!
# CMDSWITCHAUDIOIFACE="%CMDSWITCHAUDIOIFACE%"
# ### Play custom playlist --> does not seem to be implemented (or rather only links to a single specifc folder)
# With new concept, simply choose a folder with m3u inside
# CMDPLAYCUSTOMPLS="%CMDPLAYCUSTOMPLS%"
