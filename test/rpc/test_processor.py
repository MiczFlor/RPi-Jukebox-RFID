import copy
import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import Mock

import pytest

from jukebox.rpc import processor


def test_successful_request_passes_all_call_parameters(monkeypatch):
    call = Mock(return_value='done')
    monkeypatch.setattr(processor.plugs, 'call', call)
    request = {
        'package': 'player',
        'plugin': 'ctrl',
        'method': 'play',
        'args': ['album'],
        'kwargs': {'shuffle': True},
        'as_thread': False,
        'id': 'request-1',
    }

    assert processor.process_request(request) == {
        'result': 'done',
        'id': 'request-1',
    }
    call.assert_called_once_with(
        'player',
        'ctrl',
        'play',
        args=['album'],
        kwargs={'shuffle': True},
        as_thread=False,
    )


def test_request_without_id_discards_result(monkeypatch):
    monkeypatch.setattr(processor.plugs, 'call', lambda *args, **kwargs: 'done')

    response = processor.process_request({'package': 'player', 'plugin': 'ctrl'})

    assert response == {'result': None}


@pytest.mark.parametrize(
    ('rpc_request', 'message'),
    [
        ({}, "Missing mandatory parameter 'package'."),
        ({'package': 'player'}, "Missing mandatory parameter 'plugin'."),
    ],
)
def test_missing_mandatory_fields(monkeypatch, rpc_request, message):
    call = Mock()
    monkeypatch.setattr(processor.plugs, 'call', call)

    response = processor.process_request(rpc_request)

    assert response == {'error': {'code': -1, 'message': message}}
    call.assert_not_called()


def test_plugin_error_retains_request_id(monkeypatch):
    def fail(*args, **kwargs):
        raise ValueError('bad call')

    monkeypatch.setattr(processor.plugs, 'call', fail)

    response = processor.process_request({
        'package': 'player',
        'plugin': 'ctrl',
        'id': 42,
    })

    assert response == {
        'error': {'code': -1, 'message': 'ValueError: bad call'},
        'id': 42,
    }


def test_unknown_keys_are_ignored(monkeypatch, caplog):
    monkeypatch.setattr(processor.plugs, 'call', lambda *args, **kwargs: 'done')

    with caplog.at_level(logging.WARNING, logger='jb.rpc.processor'):
        response = processor.process_request({
            'package': 'player',
            'plugin': 'ctrl',
            'id': 'id',
            'future-option': True,
        })

    assert response == {'result': 'done', 'id': 'id'}
    assert "['future-option']" in caplog.text


@pytest.mark.parametrize('rpc_request', [None, [], 'request'])
def test_non_object_request_returns_error(rpc_request):
    response = processor.process_request(rpc_request)

    assert response == {
        'error': {'code': -1, 'message': 'RPC request must be an object.'},
    }


def test_processing_does_not_mutate_input(monkeypatch):
    request = {
        'package': 'player',
        'plugin': 'ctrl',
        'args': [['original']],
        'kwargs': {'settings': {'volume': 10}},
        'id': {'nested': 'id'},
    }
    original = copy.deepcopy(request)

    def mutate_plugin_inputs(*args, **kwargs):
        kwargs['args'][0].append('changed')
        kwargs['kwargs']['settings']['volume'] = 99
        return 'done'

    monkeypatch.setattr(processor.plugs, 'call', mutate_plugin_inputs)

    assert processor.process_request(request)['result'] == 'done'
    assert request == original


def test_timestamp_is_reported_without_mutating_request(monkeypatch):
    monkeypatch.setattr(processor.plugs, 'call', lambda *args, **kwargs: None)
    request = {
        'package': 'player',
        'plugin': 'ctrl',
        'tsp': 1_000_000,
        'id': 'id',
    }

    response = processor.process_request(request, received_at_ns=2_500_000)

    assert response['total_processing_time'] == 1.5
    assert request['tsp'] == 1_000_000


def test_plugin_execution_remains_serialized_across_transports(monkeypatch):
    active_calls = 0
    max_active_calls = 0
    activity_lock = threading.Lock()

    def slow_call(*args, **kwargs):
        nonlocal active_calls, max_active_calls
        with activity_lock:
            active_calls += 1
            max_active_calls = max(max_active_calls, active_calls)
        time.sleep(0.02)
        with activity_lock:
            active_calls -= 1
        return 'done'

    monkeypatch.setattr(processor.plugs, '_call', slow_call)
    requests = [
        {'package': 'player', 'plugin': 'ctrl', 'id': transport}
        for transport in ('http', 'zmq')
    ]

    with ThreadPoolExecutor(max_workers=2) as executor:
        responses = list(executor.map(processor.process_request, requests))

    assert [response['result'] for response in responses] == ['done', 'done']
    assert max_active_calls == 1
