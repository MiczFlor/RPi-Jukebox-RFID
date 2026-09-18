from components.rfid.cardutils import decode_card_command


def test_provider_card_routes_to_play_card():
    action = decode_card_command({
        'provider': 'jellyfin',
        'value': 'service:jellyfin:album:abc123',
    })

    assert action == {
        'package': 'player',
        'plugin': 'ctrl',
        'method': 'play_card',
        'args': ('service:jellyfin:album:abc123',),
        'kwargs': {'provider': 'jellyfin'},
    }


def test_provider_card_track_uri():
    action = decode_card_command({
        'provider': 'jellyfin',
        'value': 'service:jellyfin:track:xyz789',
        'recursive': False,
    })

    assert action['method'] == 'play_card'
    assert action['args'] == ('service:jellyfin:track:xyz789',)
    assert action['kwargs'] == {'provider': 'jellyfin'}


def test_provider_card_recursive_flag():
    action = decode_card_command({
        'provider': 'jellyfin',
        'value': 'service:jellyfin:album:abc123',
        'recursive': True,
    })

    assert action['kwargs'] == {'recursive': True, 'provider': 'jellyfin'}


def test_legacy_play_card_alias_keeps_current_behavior():
    action = decode_card_command({
        'alias': 'play_card',
        'args': ['stories/chapter-one'],
    })

    assert action == {
        'package': 'player',
        'plugin': 'ctrl',
        'method': 'play_card',
        'args': ('stories/chapter-one',),
        'kwargs': {},
    }


def test_legacy_play_folder_alias_routes_recursive():
    action = decode_card_command({
        'alias': 'play_folder',
        'args': ['stories', True],
    })

    assert action['method'] == 'play_card'
    assert action['args'] == ('stories',)
    assert action['kwargs'] == {'recursive': True}


def test_command_card_routing_is_unchanged():
    action = decode_card_command({'alias': 'shutdown'})

    assert action['package'] == 'host'
    assert action['plugin'] == 'shutdown'


def test_provider_card_without_name_is_rejected():
    action = decode_card_command({
        'provider': '',
        'value': 'service:jellyfin:album:abc123',
    })

    assert action is None


def test_provider_card_without_value_is_rejected():
    action = decode_card_command({
        'provider': 'jellyfin',
        'value': '',
    })

    assert action is None


def test_card_specific_options_are_preserved_for_provider_cards():
    action = decode_card_command({
        'provider': 'jellyfin',
        'value': 'service:jellyfin:track:xyz789',
        'ignore_same_id_delay': True,
        'ignore_card_removal_action': True,
    })

    assert action['ignore_same_id_delay'] is True
    assert action['ignore_card_removal_action'] is True


def test_card_specific_options_are_preserved_for_legacy_cards():
    action = decode_card_command({
        'alias': 'play_card',
        'args': ['stories/chapter-one'],
        'ignore_same_id_delay': True,
    })

    assert action['ignore_same_id_delay'] is True


def test_mpd_provider_card_omits_provider_argument():
    action = decode_card_command({
        'provider': 'mpd',
        'value': 'stories/chapter-one',
    })

    assert action['method'] == 'play_card'
    assert action['args'] == ('stories/chapter-one',)
    assert action['kwargs'] == {}
