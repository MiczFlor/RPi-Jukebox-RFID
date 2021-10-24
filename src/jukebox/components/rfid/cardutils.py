"""
Common card decoding functions

TODO: Thread safety when accessing the card DB!
"""


import logging
from typing import (List, Mapping)
import jukebox.utils as utils
import jukebox.cfghandler

log = logging.getLogger('jb.cardutils')
cfg_cards = jukebox.cfghandler.get_handler('cards')


def decode_card_command(cfg_rpc_cmd: Mapping, logger: logging.Logger = log):
    """Extension of utils.decode_action with card-specific parameters"""
    action = utils.decode_rpc_command(cfg_rpc_cmd, logger)
    if 'ignore_same_id_delay' in cfg_rpc_cmd:
        action['ignore_same_id_delay'] = cfg_rpc_cmd['ignore_same_id_delay']
    if 'ignore_card_removal_action' in cfg_rpc_cmd:
        action['ignore_card_removal_action'] = cfg_rpc_cmd['ignore_card_removal_action']
    return action


def card_command_to_str(cfg_rpc_cmd: Mapping, long=False) -> List[str]:
    """Returns a list of strings with [card_action, ignore_same_id_delay, ignore_card_removal_action]

    The last two parameters are only present, if *long* is True and if they are present in the cfg_rpc_cmd"""
    action = decode_card_command(cfg_rpc_cmd)
    readable = [utils.rpc_call_to_str(action)]
    if long:
        if 'ignore_same_id_delay' in action.keys():
            readable.append(f"ignore_same_id_delay: {action['ignore_same_id_delay']}")
        if 'ignore_card_removal_action' in action.keys():
            readable.append(f"ignore_card_removal_action: {action['ignore_card_removal_action']}")
    return readable


def card_to_str(card_id: str, long=False) -> List[str]:
    """Returns a list of strings from card entry command in the format of :func:`card_command_to_str`"""
    readable = ["Error: Card ID not found in database!"]
    if card_id in cfg_cards:
        readable = card_command_to_str(cfg_cards.getn(card_id, default=None), long)
    return readable
