"""
Handling the RFID card database

A few considerations:
- Changing the Card DB influences to current state
  - rfid.reader: Does not care, as it always freshly looks into the DB when a new card is triggered
  - fake_reader_gui: Initializes the Drop-down menu once on start --> Will get out of date!

Do we need a notifier? Or a callback for modules to get notified?
Do we want to publish the information about a card DB update?
TODO: Add callback for on_database_change
"""

import logging
import time
from typing import (List, Dict, Optional)
import jukebox.utils as utils
import jukebox.cfghandler
import jukebox.plugs as plugs
import jukebox.publishing as publishing
from components.rfid.cardactions import (qs_action_place, qs_action_remove)
from components.rfid.cardutils import decode_card_action
from components.rfid.cardutils import (dump_card_action_reference)


log = logging.getLogger('jb.cards')
cfg_cards = jukebox.cfghandler.get_handler('cards')
cfg_main = jukebox.cfghandler.get_handler('jukebox')


@plugs.register
def list_cards():
    """Provide a summarized, decoded list of all card actions

    This is intended as basis for a formatter function

    Format: 'id': {decoded_function_call, ignore_same_id_delay, ignore_card_removal_action, description, from_quick_select}"""
    card_list = {}
    with cfg_cards:
        for card_id, card_action in cfg_cards.items():
            action = decode_card_action(card_action, qs_action_place)

            try:
                func = plugs.get(action['package'], action['plugin'], action.get('method', None))
            except Exception as e:
                description = f"ERROR: {e.__class__.__name__}: {e}"
            else:
                description = (func.__doc__ or "").split('\n\n', 1)[0].strip('\n ')
            readable = utils.action_to_str(action)

            card_list[card_id] = {
                'func': readable,
                'description': description,
                'action': action
            }

            if 'ignore_same_id_delay' in action.keys():
                card_list[card_id]['ignore_same_id_delay'] = action['ignore_same_id_delay']
            if 'ignore_card_removal_action' in action.keys():
                card_list[card_id]['ignore_card_removal_action'] = action['ignore_card_removal_action']
            qs = card_action.get('quick_select', None)
            if qs is not None:
                card_list[card_id]['from_quick_select'] = qs
    return card_list


@plugs.register
def delete_card(card_id: str, auto_save: bool = True):
    """

    :param auto_save:
    :param card_id:
    """
    # Make it thread safe: Lock the database
    with cfg_cards:
        if card_id in cfg_cards.keys():
            del cfg_cards[card_id]
            if auto_save:
                cfg_cards.save()
        else:
            msg = f"Attempt to delete non-existing key: {card_id}"
            log.error(msg)
            raise KeyError(msg)
    publishing.get_publisher().send(f'{plugs.loaded_as(__name__)}.database.has_changed', time.ctime())


@plugs.register
def register_card(card_id: str, quick_select: str,
                  args: Optional[List] = None, kwargs: Optional[Dict] = None,
                  ignore_card_removal_action: Optional[bool] = None, ignore_same_id_delay: Optional[bool] = None,
                  overwrite: bool = False,
                  auto_save: bool = True):
    """Register a new card based on quick-selection

    If you are going to call this through the RPC it will get a little verbose

    **Example:** Registering a new card with ID *0009* for increment volume with a custom argument to inc_volume
    (*here: 15*) and custom *ignore_same_id_delay value*::

        plugin.call_ignore_errors('cards', 'register_card',
                                  args=['0009', 'inc_volume'],
                                  kwargs={'args': [15], 'ignore_same_id_delay': True, 'overwrite': True})

    """
    if quick_select not in qs_action_place.keys():
        msg = f"Unknown quick_select: '{quick_select}'"
        log.error(msg)
        raise KeyError(msg)
    with cfg_cards:
        if not overwrite and card_id in cfg_cards.keys():
            msg = f"Card already registered: '{card_id}'. Abort. (use overwrite=True to overrule)"
            log.error(msg)
            raise KeyError(msg)
        cfg_cards[card_id] = {'quick_select': quick_select}
        if args is not None:
            cfg_cards[card_id]['args'] = args
        if kwargs is not None:
            cfg_cards[card_id]['kwargs'] = args
        if ignore_same_id_delay is not None:
            cfg_cards[card_id]['ignore_same_id_delay'] = ignore_same_id_delay
        if ignore_card_removal_action is not None:
            cfg_cards[card_id]['ignore_card_removal_action'] = ignore_card_removal_action
        if auto_save:
            cfg_cards.save()
    publishing.get_publisher().send(f'{plugs.loaded_as(__name__)}.database.has_changed', time.ctime())


@plugs.register
def register_card_custom():
    """Register a new card with full RPC call specification (Not implemented yet)"""
    raise NotImplementedError


def check_card_database():
    with cfg_cards:
        # Check type of keys (all of them)
        illegal_cards = [x for x in cfg_cards.keys() if not isinstance(x, str)]
        if len(illegal_cards) > 0:
            log.error(f"Found non-string card ID entries! Ignoring the following cards IDs: {illegal_cards}")
            # TODO: Further checks for illegal entries?


@plugs.register
def load_card_database(filename):
    try:
        jukebox.cfghandler.load_yaml(cfg_cards, filename)
    except FileNotFoundError:
        cfg_cards.config_dict({})
        log.error(f"Empty card database: Could not open file: {filename}")
    check_card_database()
    publishing.get_publisher().send(f'{plugs.loaded_as(__name__)}.database.has_changed', time.ctime())


@plugs.register
def save_card_database(filename=None, *, only_if_changed=True):
    """Store the current card database. If filename is None, it is saved back to the file it was loaded from"""
    if filename is None:
        cfg_cards.save(only_if_changed=only_if_changed)
    else:
        jukebox.cfghandler.write_yaml(cfg_cards, filename, only_if_changed=only_if_changed)


@plugs.finalize
def finalize():
    load_card_database(cfg_main.getn('rfid', 'card_database'))

    # Write reference of command shortcuts
    if 'card_action_reference_out' in cfg_main['rfid']:
        with open(cfg_main.getn('rfid', 'card_action_reference_out'), 'w') as stream:
            dump_card_action_reference(stream, qs_action_place, 'Card placement action shortcuts')
            print('\n\n', file=stream)
            dump_card_action_reference(stream, qs_action_remove, 'Card removal action shortcuts (only place-capable readers)')


@plugs.atexit
def atexit(**ignored_kwargs):
    save_card_database(only_if_changed=True)
