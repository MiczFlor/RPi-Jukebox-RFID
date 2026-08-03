import importlib.util
from pathlib import Path

import pytest

SERVER_PATH = (
    Path(__file__).parents[2]
    / 'src'
    / 'jukebox'
    / 'jukebox'
    / 'publishing'
    / 'server.py'
)
SPEC = importlib.util.spec_from_file_location('publishing_server_under_test', SERVER_PATH)
server_module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(server_module)
LastValueCache = server_module.LastValueCache


@pytest.mark.parametrize('initial_payload', [None, b'47.2'])
def test_cache_revocation_is_idempotent(initial_payload):
    cache = LastValueCache(frontend=None, backend=None)
    topic = b'host.temperature.cpu'
    if initial_payload is not None:
        cache.update(topic, initial_payload)

    cache.update(topic, b'')
    cache.update(topic, b'')

    assert topic not in cache.cache
