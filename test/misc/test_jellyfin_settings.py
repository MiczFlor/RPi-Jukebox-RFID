"""Tests for the Jellyfin settings RPCs in the misc plugin package.

The functions are exercised directly instead of through ``plugs.call``: the
evdev tests replace ``plugs.register`` with a no-op decorator at module level
for the whole session, so plugin registration cannot be relied upon here.
"""

import pytest

import jukebox.cfghandler as cfghandler
import jukebox.plugs as plugs

# Import the misc plugin module directly: the evdev tests replace
# ``plugs.register`` with a no-op decorator for the whole session, so plugin
# loading cannot be relied on here.
plugs.ALLOW_DIRECT_IMPORTS = True
import components.misc as misc  # noqa: E402


@pytest.fixture(autouse=True)
def empty_config():
    cfg = cfghandler.get_handler('jukebox')
    cfg.config_dict({})
    yield
    cfg.config_dict({})


def test_get_jellyfin_settings_returns_defaults_without_secrets():
    settings = misc.get_jellyfin_settings()

    assert settings['enabled'] is False
    assert settings['host'] == ''
    assert settings['username'] == ''
    assert settings['has_api_key'] is False
    assert settings['has_password'] is False
    assert settings['catalog_cache_ttl'] == 300
    assert settings['request_timeout'] == 30
    # The secrets themselves must never leave the backend.
    assert 'api_key' not in settings
    assert 'password' not in settings


def test_get_jellyfin_settings_reports_secrets_as_set_only():
    cfg = cfghandler.get_handler('jukebox')
    cfg.setn('players', 'jellyfin', 'api_key', value='stored-key')
    cfg.setn('players', 'jellyfin', 'password', value='stored-pw')

    settings = misc.get_jellyfin_settings()

    assert settings['has_api_key'] is True
    assert settings['has_password'] is True
    assert 'api_key' not in settings
    assert 'password' not in settings


def test_set_jellyfin_settings_updates_values():
    misc.set_jellyfin_settings({
        'enabled': True,
        'host': 'http://jellyfin.local:8096',
        'username': 'user',
        'password': 'pw',
        'catalog_cache_ttl': 120,
        'request_timeout': 45,
    })

    settings = misc.get_jellyfin_settings()
    assert settings['enabled'] is True
    assert settings['host'] == 'http://jellyfin.local:8096'
    assert settings['username'] == 'user'
    assert settings['has_password'] is True
    assert settings['catalog_cache_ttl'] == 120.0
    assert settings['request_timeout'] == 45.0
    assert 'password' not in settings


def test_set_jellyfin_settings_empty_secret_keeps_stored_value():
    cfg = cfghandler.get_handler('jukebox')
    cfg.setn('players', 'jellyfin', 'api_key', value='stored-key')

    # An empty secret must not clear the stored value.
    misc.set_jellyfin_settings({'api_key': ''})
    assert misc.get_jellyfin_settings()['has_api_key'] is True

    # A new non-empty value overwrites the stored secret.
    misc.set_jellyfin_settings({'api_key': 'new-key'})
    assert misc.get_jellyfin_settings()['has_api_key'] is True


def test_set_jellyfin_settings_rejects_unknown_keys():
    with pytest.raises(ValueError):
        misc.set_jellyfin_settings({'bogus': True})


def test_set_jellyfin_settings_validates_numeric_values():
    with pytest.raises(ValueError):
        misc.set_jellyfin_settings({'catalog_cache_ttl': 'abc'})
    with pytest.raises(ValueError):
        misc.set_jellyfin_settings({'request_timeout': 0})


def test_set_jellyfin_settings_validates_enabled_requirements():
    with pytest.raises(ValueError):
        misc.set_jellyfin_settings(
            {'enabled': True, 'host': ''})
    with pytest.raises(ValueError):
        misc.set_jellyfin_settings(
            {'enabled': True, 'host': 'http://jellyfin.local:8096'})

    # A username/password pair makes the enabled configuration valid.
    misc.set_jellyfin_settings({
        'enabled': True,
        'host': 'http://jellyfin.local:8096',
        'username': 'user',
        'password': 'pw',
    })
    assert misc.get_jellyfin_settings()['enabled'] is True


def test_set_jellyfin_settings_accepts_existing_credentials_when_enabling():
    cfg = cfghandler.get_handler('jukebox')
    cfg.setn('players', 'jellyfin', 'api_key', value='stored-key')

    # Enabling with only the host works when a credential is already stored.
    misc.set_jellyfin_settings(
        {'enabled': True, 'host': 'http://jellyfin.local:8096'})
    assert misc.get_jellyfin_settings()['enabled'] is True


def test_jellyfin_connection_expands_and_probes(monkeypatch):
    import components.jellyfin.jellyfin_api_client as api_client
    monkeypatch.setattr(
        api_client, 'probe_jellyfin_host',
        lambda candidates, timeout=3.0: candidates[2])

    result = misc.test_jellyfin_connection('192.168.1.10')

    assert result['found'] is True
    assert result['url'] == 'http://192.168.1.10:8920'
    assert result['candidates'] == [
        'http://192.168.1.10:8096',
        'https://192.168.1.10:8920',
        'http://192.168.1.10:8920',
        'https://192.168.1.10:8096',
    ]


def test_jellyfin_connection_reports_not_found(monkeypatch):
    import components.jellyfin.jellyfin_api_client as api_client
    monkeypatch.setattr(
        api_client, 'probe_jellyfin_host',
        lambda candidates, timeout=3.0: None)

    result = misc.test_jellyfin_connection('192.168.1.10')

    assert result['found'] is False
    assert result['url'] is None
    assert len(result['candidates']) == 4


def test_jellyfin_connection_empty_host_returns_no_candidates(
        monkeypatch):
    import components.jellyfin.jellyfin_api_client as api_client
    monkeypatch.setattr(
        api_client, 'probe_jellyfin_host',
        lambda candidates, timeout=3.0: pytest.fail(
            'probe must not run without candidates'))

    result = misc.test_jellyfin_connection('')

    assert result == {'found': False, 'url': None, 'candidates': []}
