import logging
import functools
import re
import jukebox.utils as utils
import jukebox.cfghandler
from components.rfid.cardactions import (qs_action_place)

log = logging.getLogger('jb.cardutilss')
cfg_cards = jukebox.cfghandler.get_handler('cards')


def decode_card_action(cfg_action, quick_select_dict=None, logger=log):
    """Extension of utils.deocde_action with card-specific parameters"""
    action = utils.decode_action(cfg_action, quick_select_dict, logger)
    if 'ignore_same_id_delay' in cfg_action:
        action['ignore_same_id_delay'] = cfg_action['ignore_same_id_delay']
    if 'ignore_card_removal_action' in cfg_action:
        action['ignore_card_removal_action'] = cfg_action['ignore_card_removal_action']
    return action


def card_action_to_str(cfg_action, long=False, multiline=False) -> str:
    action = decode_card_action(cfg_action, qs_action_place)
    readable = utils.action_to_str(action)
    if long:
        if 'ignore_same_id_delay' in action.keys():
            readable += '\n' if multiline else ' / '
            readable += f"ignore_same_id_delay: {action['ignore_same_id_delay']}"
        if 'ignore_card_removal_action' in action.keys():
            readable += '\n' if multiline else ' / '
            readable += f"ignore_card_removal_action: {action['ignore_card_removal_action']}"
    return readable


def card_to_str(card_id, long=False, multiline=False) -> str:
    """Format a readable string from card entry command"""
    readable = "Error: Card ID not found in database!"
    if card_id in cfg_cards:
        readable = card_action_to_str(cfg_cards.getn(card_id, default=None), long, multiline)
    return readable


def dump_card_action_reference(stream, quick_selection_lookup, name):
    """Write a human readable summary of all card action shortcuts"""
    width = 127
    print('*' * width, file=stream)
    print(f"{name}", file=stream)
    print('*' * width, file=stream)
    cmd_max_len = functools.reduce(lambda x, y: max(x, len(y)), quick_selection_lookup.keys(), 0)
    # A bit of a quick hack for multiline formatting:
    # Parameters starting with ignore will be indented.
    # This assumes (a) there are no other parameters and (b) no command starts with 'ignore'
    pattern = re.compile(r'^\s*ignore', re.MULTILINE)
    for cmd, action in quick_selection_lookup.items():
        readable = card_action_to_str(action, long=True, multiline=True)
        readable = pattern.sub(f"{' ' * cmd_max_len}     ignore", readable)
        print(f"{cmd:<{cmd_max_len}}: {readable}", file=stream)
    print('*' * width, file=stream)
