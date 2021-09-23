"""
Common card decoding functions

TODO: Thread safety when accessing the card DB!
"""


import logging
import inspect
from typing import (List)
import jukebox.utils as utils
import jukebox.cfghandler
import jukebox.plugs as plugs
from components.rfid.cardactions import (qs_action_place)

log = logging.getLogger('jb.cardutils')
cfg_cards = jukebox.cfghandler.get_handler('cards')


def decode_card_action(cfg_action, quick_select_dict=None, logger=log):
    """Extension of utils.decode_action with card-specific parameters"""
    action = utils.decode_action(cfg_action, quick_select_dict, logger)
    if 'ignore_same_id_delay' in cfg_action:
        action['ignore_same_id_delay'] = cfg_action['ignore_same_id_delay']
    if 'ignore_card_removal_action' in cfg_action:
        action['ignore_card_removal_action'] = cfg_action['ignore_card_removal_action']
    return action


def card_action_to_str(cfg_action, long=False) -> List[str]:
    """Returns a list of strings with [card_action, ignore_same_id_delay, ignore_card_removal_action]"""
    action = decode_card_action(cfg_action, qs_action_place)
    readable = [utils.action_to_str(action)]
    if long:
        if 'ignore_same_id_delay' in action.keys():
            readable.append(f"ignore_same_id_delay: {action['ignore_same_id_delay']}")
        if 'ignore_card_removal_action' in action.keys():
            readable.append(f"ignore_card_removal_action: {action['ignore_card_removal_action']}")
    return readable


def card_to_str(card_id, long=False) -> List[str]:
    """Format a readable string from card entry command"""
    readable = ["Error: Card ID not found in database!"]
    if card_id in cfg_cards:
        readable = card_action_to_str(cfg_cards.getn(card_id, default=None), long)
    return readable


def dump_card_action_reference(stream, quick_selection_lookup, name):
    """Write a human readable summary of all card action shortcuts"""
    width = 127
    print('*' * width, file=stream)
    print(f"{name}", file=stream)
    print('*' * width, file=stream)
    print("\n", file=stream)
    for cmd, action in quick_selection_lookup.items():
        try:
            func = plugs.get(action['package'], action['plugin'], action.get('method', None))
        except Exception as e:
            description = f"ERROR: {e.__class__.__name__}: {e}"
            signature = "(---UNKNOWN---)"
        else:
            description = (func.__doc__ or "").split('\n\n', 1)[0].strip('\n ')
            signature = inspect.signature(func)
        readable = card_action_to_str(action, long=True)
        print(f"'{cmd}':", file=stream)
        print(f"   Executes   : {readable[0]}", file=stream)
        for idx in range(1, len(readable)):
            print(f"                {readable[idx]}", file=stream)
        print(f"   Signature  : {utils.action_to_str(action, with_args=False)}{signature}", file=stream)
        print(f"   Description: {description}\n", file=stream)
    print('*' * width, file=stream)
