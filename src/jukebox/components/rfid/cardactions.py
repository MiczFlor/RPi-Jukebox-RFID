"""
This file provides definitions for card action quick selections

A card action can be any RPC call with arbitrary parameters. Additionally, card_behaviour parameters can be added.

But that involves setting up to 6 configuration parameters per card entry.
Which is a bit excessive for the often used functions. The solution is these quick_select actions.

How it works:
Instead of specified the full RPC call, simply specify
'card_id':
  quick_select: play_card
  args = [MusicFolder]

For every quick select the parameters args, kwargs, ignore_card_removal_action, ignore_same_id_delay can be overridden
in the card config.

# Example: Increment volume by default step, ignore_card_removal_action = True (default), ignore_same_id_delay = True (default)
'card_id':
  quick_select: inc_volume

# Example: Increment volume by custom step, ignore_card_removal_action = True (default), ignore_same_id_delay = False (custom)
'card_id':
  quick_select: inc_volume
  args = [5]
  ignore_same_id_delay: False
"""

# TODO: Transfer RFID command from v2.3...

# --------------------------------------------------------------
# Pre-defined actions for card placement / trigger
# --------------------------------------------------------------
qs_action_place = {
    # Trigger the playback of a card (second swipe is handled by this function as part of the player)
    # This is function you'll want to use most often
    'play_card': {'package': 'player',
                  'plugin': 'ctrl',
                  'method': 'play_card'},
    # Increment volume a little bit (for place-capable readers as long as card is on reader)
    'inc_volume': {'package': 'volume',
                   'plugin': 'ctrl',
                   'method': 'inc_volume',
                   'ignore_card_removal_action': True,
                   'ignore_same_id_delay': True},
    'dec_volume': {'package': 'volume',
                   'plugin': 'ctrl',
                   'method': 'inc_volume',
                   'args': [5],
                   'ignore_card_removal_action': True,
                   'ignore_same_id_delay': True},
    'shutdown': {'package': 'host',
                 'plugin': 'shutdown'},
    'reboot': {'package': 'host',
               'plugin': 'reboot'}
}

# --------------------------------------------------------------
# Pre-defined actions for card removal
# --------------------------------------------------------------
qs_action_remove = {
    # Pause the playback, so it can be resumed when card is placed on the reader again
    # (if card placement triggers play_card and second_swipe is off or configured to play)
    'pause': {'package': 'player',
              'plugin': 'ctrl',
              'method': 'pause'}
}
