"""Tests for the persistent Jellyfin token store."""

import json
import stat

import pytest

from components.jellyfin.jellyfin_token_store import JellyfinTokenStore


USERNAME = 'phoniebox'
DEVICE_ID = 'device-1'
TOKEN = 'access-token'
USER_ID = 'user-id'


def make_store(tmp_path, name='jellyfin_token.json'):
    """Return a store whose file lives in tmp_path."""
    return JellyfinTokenStore(tmp_path / name)


def save_token(store, username=USERNAME, device_id=DEVICE_ID):
    """Store a token for the given identity."""
    store.save(TOKEN, USER_ID, username, device_id)


def read_payload(store):
    """Return the stored mapping."""
    return json.loads(store.path.read_text(encoding='utf-8'))


def test_load_returns_nothing_without_file(tmp_path):
    store = make_store(tmp_path)

    assert store.load(USERNAME, DEVICE_ID) == (None, None)


def test_save_and_load_round_trip(tmp_path):
    store = make_store(tmp_path)

    save_token(store)

    assert store.load(USERNAME, DEVICE_ID) == (TOKEN, USER_ID)
    payload = read_payload(store)
    assert payload['access_token'] == TOKEN
    assert payload['user_id'] == USER_ID
    assert payload['token_username'] == USERNAME
    assert payload['token_device_id'] == DEVICE_ID


def test_token_for_other_user_is_discarded(tmp_path):
    store = make_store(tmp_path)
    save_token(store)

    assert store.load('someone-else', DEVICE_ID) == (None, None)


def test_token_for_other_device_is_discarded(tmp_path):
    store = make_store(tmp_path)
    save_token(store)

    assert store.load(USERNAME, 'other-device') == (None, None)


def test_identity_mismatch_leaves_the_file_untouched(tmp_path):
    store = make_store(tmp_path)
    save_token(store)
    before = store.path.read_text(encoding='utf-8')

    store.load('someone-else', 'other-device')

    assert store.path.read_text(encoding='utf-8') == before


def test_clear_removes_token_and_identity_but_keeps_device_id(tmp_path):
    store = make_store(tmp_path)
    device_id = store.device_id()
    save_token(store, device_id=device_id)

    store.clear()

    assert store.load(USERNAME, device_id) == (None, None)
    assert store.device_id() == device_id
    payload = read_payload(store)
    assert 'access_token' not in payload
    assert 'user_id' not in payload
    assert 'token_username' not in payload
    assert 'token_device_id' not in payload


def test_clear_without_file_is_a_noop(tmp_path):
    store = make_store(tmp_path)

    store.clear()

    assert not store.path.exists()


def test_device_id_is_generated_and_persisted(tmp_path):
    store = make_store(tmp_path)

    device_id = store.device_id()

    assert device_id
    assert JellyfinTokenStore(store.path).device_id() == device_id
    assert read_payload(store)['device_id'] == device_id


def test_configured_device_id_wins_and_is_persisted(tmp_path):
    store = make_store(tmp_path)
    store.device_id()

    assert store.device_id('configured-id') == 'configured-id'
    assert JellyfinTokenStore(store.path).device_id() == 'configured-id'


def test_changing_the_device_id_discards_the_stored_token(tmp_path):
    store = make_store(tmp_path)
    old_device_id = store.device_id()
    save_token(store, device_id=old_device_id)

    store.device_id('configured-id')

    assert store.load(USERNAME, 'configured-id') == (None, None)
    assert store.load(USERNAME, old_device_id) == (TOKEN, USER_ID)


def test_two_stores_yield_different_device_ids(tmp_path):
    first = make_store(tmp_path, 'first.json')
    second = make_store(tmp_path, 'second.json')

    assert first.device_id() != second.device_id()


def test_store_creates_the_parent_directory(tmp_path):
    store = make_store(tmp_path, 'nested/dir/token.json')

    save_token(store)

    assert store.load(USERNAME, DEVICE_ID) == (TOKEN, USER_ID)


def test_file_is_written_with_mode_0600(tmp_path):
    store = make_store(tmp_path)

    save_token(store)

    assert stat.S_IMODE(store.path.stat().st_mode) == 0o600


def test_corrupt_file_yields_no_token_and_is_overwritten(tmp_path):
    store = make_store(tmp_path)
    store.path.write_text('{not json', encoding='utf-8')

    assert store.load(USERNAME, DEVICE_ID) == (None, None)

    save_token(store)

    assert store.load(USERNAME, DEVICE_ID) == (TOKEN, USER_ID)


def test_non_mapping_payload_yields_no_token(tmp_path):
    store = make_store(tmp_path)
    store.path.write_text('[1, 2, 3]', encoding='utf-8')

    assert store.load(USERNAME, DEVICE_ID) == (None, None)


def test_unwritable_path_raises_oserror(tmp_path):
    directory = tmp_path / 'blocked'
    directory.mkdir()
    store = JellyfinTokenStore(directory)

    with pytest.raises(OSError):
        save_token(store)

    assert store.load(USERNAME, DEVICE_ID) == (None, None)
    assert list(tmp_path.iterdir()) == [directory]
