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

#: Legacy card aliases that always play on the default (local) backend.
PLAYBACK_ALIASES = ('play_card', 'play_folder')


def _resolve_provider(cfg_rpc_cmd: Mapping, logger: logging.Logger = log):
    """Resolve the target player backend for a playback card entry.

    Playback cards are either written explicitly as ``provider`` + ``value``
    pairs, or implicitly as the legacy ``play_card`` / ``play_folder`` aliases
    that always target the default (local) backend.

    Both legacy aliases are dispatched through ``player.ctrl.play_card`` (the
    coordinator runs second-swipe detection and the card callbacks there); the
    ``play_folder`` alias deliberately no longer maps to
    ``player.ctrl.play_folder``. Only ``provider``-qualified cards can target
    a non-default backend.

    :return: ``(provider_name, value, recursive, is_legacy)``. ``provider_name``
        is ``None`` for cards that are not playback cards.
    """
    if 'provider' in cfg_rpc_cmd:
        provider_name = cfg_rpc_cmd['provider']
        value = cfg_rpc_cmd.get('value', '')
        recursive = cfg_rpc_cmd.get('recursive', False)
        if not provider_name:
            logger.error("Card entry has 'provider:' but no provider name")
            return (None, '', False, False)
        if not value:
            logger.error(f"Card entry for provider '{provider_name}' has no 'value'")
            return (None, '', False, False)
        return (provider_name, value, recursive, False)
    alias = cfg_rpc_cmd.get('alias')
    if alias in PLAYBACK_ALIASES:
        args = cfg_rpc_cmd.get('args', [])
        value = args[0] if args else ''
        recursive = len(args) > 1 and args[1] is True
        return ('mpd', value, recursive, True)
    return (None, '', False, False)


def decode_card_command(cfg_rpc_cmd: Mapping, logger: logging.Logger = log):
    """Extension of utils.decode_action with card-specific parameters"""
    if cfg_rpc_cmd is None:
        return None
    provider_name, value, recursive, _is_legacy = _resolve_provider(cfg_rpc_cmd, logger)
    if provider_name is not None:
        # The emitted command routes through player.ctrl.play_card(value,
        # provider=...); an unknown provider is reported by the coordinator at
        # dispatch time. Both legacy aliases (play_card and play_folder) are
        # dispatched through play_card here, so second-swipe detection and the
        # card callbacks apply to them. Legacy mpd cards keep their current
        # behavior by not passing a provider argument at all.
        kwargs = {'recursive': True} if recursive else {}
        if provider_name != 'mpd':
            kwargs['provider'] = provider_name
        action = {
            'package': 'player',
            'plugin': 'ctrl',
            'method': 'play_card',
            'args': (value,),
            'kwargs': kwargs,
        }
        if 'ignore_same_id_delay' in cfg_rpc_cmd:
            action['ignore_same_id_delay'] = cfg_rpc_cmd['ignore_same_id_delay']
        if 'ignore_card_removal_action' in cfg_rpc_cmd:
            action['ignore_card_removal_action'] = cfg_rpc_cmd['ignore_card_removal_action']
        return action
    if 'provider' in cfg_rpc_cmd:
        # A malformed playback card was already logged; do not decode it as a
        # generic command.
        return None
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
