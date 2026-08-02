import asyncio
import json
import socket
import threading
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta

import pytest
import tornado.gen
import tornado.httpclient
import tornado.testing
import tornado.websocket
import zmq

from jukebox.api.server import (
    ApiServer,
    EventBroker,
    MAX_MESSAGE_SIZE,
    PUBLISH_ENDPOINT,
    make_application,
)


class FakeClient:
    def __init__(self):
        self.subscriptions = set()
        self.messages = []

    def write_message(self, message):
        self.messages.append(message)
        return None


def test_broker_uses_prefix_matching_and_per_client_snapshots():
    broker = EventBroker()
    player = FakeClient()
    core = FakeClient()
    broker.publish([b'player.status', b'{"playing": true}'])
    broker.publish([b'core.version', b'"3.0"'])

    broker.register(player)
    broker.register(core)
    broker.subscribe(player, ['player'])
    broker.subscribe(core, ['core.version'])

    assert player.messages == [{
        'type': 'event',
        'topic': 'player.status',
        'data': {'playing': True},
    }]
    assert core.messages == [{
        'type': 'event',
        'topic': 'core.version',
        'data': '3.0',
    }]


def test_broker_subscribe_all_unsubscribe_and_revoke():
    broker = EventBroker()
    client = FakeClient()
    broker.register(client)
    broker.subscribe(client, [''])

    broker.publish([b'volume.level', b'12'])
    broker.publish([b'volume.level', b''])
    broker.unsubscribe(client, [''])
    broker.publish([b'volume.level', b'13'])

    assert client.messages == [
        {'type': 'event', 'topic': 'volume.level', 'data': 12},
        {'type': 'revoke', 'topic': 'volume.level'},
    ]
    assert broker.cache['volume.level'] == 13


def test_api_server_thread_lifecycle_and_stable_subscription():
    port_socket = socket.socket()
    port_socket.bind(('127.0.0.1', 0))
    port = port_socket.getsockname()[1]
    port_socket.close()

    context = zmq.Context()
    publisher = context.socket(zmq.XPUB)
    publisher.bind(PUBLISH_ENDPOINT)
    server = ApiServer(bind_address='127.0.0.1', port=port, context=context)
    try:
        server.start_and_wait()
        with urllib.request.urlopen(
            f'http://127.0.0.1:{port}/api/v1/health',
            timeout=2,
        ) as response:
            assert json.load(response) == {'status': 'ok'}

        assert publisher.poll(2000)
        assert publisher.recv() == b'\x01'

        publisher.send_multipart([b'core.version', b'"test-version"'])
        deadline = time.monotonic() + 2
        while 'core.version' not in server.broker.cache and time.monotonic() < deadline:
            time.sleep(0.01)

        async def read_snapshot():
            websocket = await tornado.websocket.websocket_connect(
                f'ws://127.0.0.1:{port}/api/v1/events',
            )
            websocket.write_message(json.dumps({
                'type': 'subscribe',
                'topics': ['core'],
            }))
            message = await tornado.gen.with_timeout(
                timedelta(seconds=2),
                websocket.read_message(),
            )
            websocket.close()
            return json.loads(message)

        assert asyncio.run(read_snapshot()) == {
            'type': 'event',
            'topic': 'core.version',
            'data': 'test-version',
        }
        assert not publisher.poll(100)
    finally:
        server.terminate()
        publisher.close(0)
        context.term()

    assert not server.is_alive()


class ApiHandlerTest(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.rpc_processor = lambda request: {
            'result': request['kwargs']['value'],
            'id': request.get('id'),
        }
        self.broker = EventBroker()
        return make_application(self.broker, self.executor, self.rpc_processor)

    def tearDown(self):
        self.executor.shutdown(wait=True, cancel_futures=True)
        super().tearDown()

    def test_health(self):
        response = self.fetch('/api/v1/health')

        assert response.code == 200
        assert json.loads(response.body) == {'status': 'ok'}

    def test_http_rpc(self):
        response = self.fetch(
            '/api/v1/rpc',
            method='POST',
            headers={'Content-Type': 'application/json; charset=utf-8'},
            body=json.dumps({'kwargs': {'value': 7}, 'id': 'request'}),
        )

        assert response.code == 200
        assert json.loads(response.body) == {'result': 7, 'id': 'request'}

    def test_http_rpc_failure_uses_envelope_with_status_200(self):
        self._app.settings['rpc_processor'] = lambda request: {
            'error': {'code': -1, 'message': 'plugin failed'},
            'id': request.get('id'),
        }
        response = self.fetch(
            '/api/v1/rpc',
            method='POST',
            headers={'Content-Type': 'application/json'},
            body=json.dumps({'id': 'request'}),
        )

        assert response.code == 200
        assert json.loads(response.body) == {
            'error': {'code': -1, 'message': 'plugin failed'},
            'id': 'request',
        }

    def test_http_rpc_rejects_invalid_content(self):
        invalid_requests = [
            ('{', 'application/json'),
            ('[]', 'application/json'),
            ('{}', 'text/plain'),
        ]
        for body, content_type in invalid_requests:
            response = self.fetch(
                '/api/v1/rpc',
                method='POST',
                headers={'Content-Type': content_type},
                body=body,
                raise_error=False,
            )

            assert response.code == 400

    def test_http_rpc_rejects_oversized_body(self):
        response = self.fetch(
            '/api/v1/rpc',
            method='POST',
            headers={'Content-Type': 'application/json'},
            body=' ' * (MAX_MESSAGE_SIZE + 1),
            raise_error=False,
        )

        assert response.code == 413

    @tornado.testing.gen_test
    async def test_websocket_origin_is_rejected(self):
        request = tornado.httpclient.HTTPRequest(
            self.get_url('/api/v1/events').replace('http:', 'ws:'),
            headers={'Origin': 'http://not-the-jukebox.invalid'},
        )

        with pytest.raises(tornado.httpclient.HTTPClientError) as error:
            await tornado.websocket.websocket_connect(request)

        assert error.value.code == 403

    @tornado.testing.gen_test
    async def test_websocket_snapshot_updates_unsubscribe_and_reconnect(self):
        self.broker.publish([b'player.status', b'{"playing": false}'])
        url = self.get_url('/api/v1/events').replace('http:', 'ws:')
        first = await tornado.websocket.websocket_connect(url)
        first.write_message(json.dumps({
            'type': 'subscribe',
            'topics': ['player'],
        }))

        snapshot = json.loads(await first.read_message())
        assert snapshot == {
            'type': 'event',
            'topic': 'player.status',
            'data': {'playing': False},
        }

        self.broker.publish([b'player.status', b'{"playing": true}'])
        update = json.loads(await first.read_message())
        assert update['data'] == {'playing': True}

        first.write_message(json.dumps({
            'type': 'unsubscribe',
            'topics': ['player'],
        }))
        await tornado.gen.sleep(0.01)
        self.broker.publish([b'player.status', b''])
        with pytest.raises(asyncio.TimeoutError):
            await tornado.gen.with_timeout(
                timedelta(milliseconds=20),
                first.read_message(),
            )
        first.close()

        second = await tornado.websocket.websocket_connect(url)
        second.write_message(json.dumps({
            'type': 'subscribe',
            'topics': ['player'],
        }))
        with pytest.raises(asyncio.TimeoutError):
            await tornado.gen.with_timeout(
                timedelta(milliseconds=20),
                second.read_message(),
            )
        second.close()

    @tornado.testing.gen_test
    async def test_blocking_rpc_does_not_block_health(self):
        started = threading.Event()
        release = threading.Event()

        def blocking_processor(request):
            started.set()
            release.wait(1)
            return {'result': 'done', 'id': request.get('id')}

        self._app.settings['rpc_processor'] = blocking_processor
        request = tornado.httpclient.HTTPRequest(
            self.get_url('/api/v1/rpc'),
            method='POST',
            headers={'Content-Type': 'application/json'},
            body=json.dumps({'id': 'request'}),
        )
        rpc_future = self.http_client.fetch(request)
        await tornado.gen.sleep(0.01)
        assert started.is_set()

        health = await self.http_client.fetch(self.get_url('/api/v1/health'))
        assert health.code == 200

        release.set()
        rpc = await rpc_future
        assert json.loads(rpc.body)['result'] == 'done'
