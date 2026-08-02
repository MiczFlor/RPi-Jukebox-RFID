import asyncio
import json
import socket
import tempfile
import threading
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from pathlib import Path

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
from jukebox.library import MusicLibrary


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
        self.library_directory = tempfile.TemporaryDirectory()
        self.library_updates = []
        self.library = MusicLibrary(
            lambda: self.library_directory.name,
            lambda: self.library_updates.append('update') or 'update-1',
        )
        return make_application(
            self.broker,
            self.executor,
            self.rpc_processor,
            library=self.library,
        )

    def tearDown(self):
        self.executor.shutdown(wait=True, cancel_futures=True)
        self.library_directory.cleanup()
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

    def test_library_upload_create_delete_and_refresh(self):
        folder_response = self.fetch(
            '/api/v1/library/folders',
            method='POST',
            headers={'Content-Type': 'application/json'},
            body=json.dumps({'parent': '.', 'name': 'Album'}),
        )
        assert folder_response.code == 201
        assert json.loads(folder_response.body) == {'path': 'Album'}

        query = urllib.parse.urlencode({'folder': 'Album', 'name': 'track.mp3'})
        upload_response = self.fetch(
            f'/api/v1/library/files?{query}',
            method='PUT',
            headers={'Content-Type': 'audio/mpeg'},
            body=b'audio data',
        )
        assert upload_response.code == 201
        assert json.loads(upload_response.body) == {
            'path': 'Album/track.mp3',
            'size': 10,
        }
        assert (
            Path(self.library_directory.name) / 'Album' / 'track.mp3'
        ).read_bytes() == b'audio data'

        list_response = self.fetch(
            '/api/v1/library/entries?folder=Album',
        )
        assert list_response.code == 200
        assert json.loads(list_response.body) == {
            'entries': [{
                'name': 'track.mp3',
                'relpath': 'Album/track.mp3',
                'type': 'file',
            }],
        }

        duplicate_response = self.fetch(
            f'/api/v1/library/files?{query}',
            method='PUT',
            body=b'replacement',
            raise_error=False,
        )
        assert duplicate_response.code == 409
        assert json.loads(duplicate_response.body)['error']['code'] == 'duplicate_name'

        refresh_response = self.fetch(
            '/api/v1/library/refresh',
            method='POST',
            body=b'',
        )
        assert refresh_response.code == 200
        assert json.loads(refresh_response.body) == {'update_id': 'update-1'}
        assert self.library_updates == ['update']

        delete_response = self.fetch(
            '/api/v1/library/entries',
            method='DELETE',
            headers={'Content-Type': 'application/json'},
            body=json.dumps({'paths': ['Album']}),
            allow_nonstandard_methods=True,
        )
        assert delete_response.code == 200
        assert json.loads(delete_response.body) == {'deleted': ['Album']}
        assert not (Path(self.library_directory.name) / 'Album').exists()

    def test_library_endpoints_reject_invalid_types_and_paths(self):
        unsupported_query = urllib.parse.urlencode({'folder': '.', 'name': 'archive.zip'})
        unsupported = self.fetch(
            f'/api/v1/library/files?{unsupported_query}',
            method='PUT',
            body=b'archive',
            raise_error=False,
        )
        assert unsupported.code == 415
        assert json.loads(unsupported.body)['error']['code'] == 'unsupported_file_type'

        traversal_query = urllib.parse.urlencode({'folder': '..', 'name': 'track.mp3'})
        traversal = self.fetch(
            f'/api/v1/library/files?{traversal_query}',
            method='PUT',
            body=b'audio',
            raise_error=False,
        )
        assert traversal.code == 400
        assert json.loads(traversal.body)['error']['code'] == 'invalid_path'

        delete_root = self.fetch(
            '/api/v1/library/entries',
            method='DELETE',
            headers={'Content-Type': 'application/json'},
            body=json.dumps({'paths': ['.']}),
            allow_nonstandard_methods=True,
            raise_error=False,
        )
        assert delete_root.code == 400
        assert json.loads(delete_root.body)['error']['code'] == 'invalid_path'

    def test_library_json_requests_remain_limited_to_one_mebibyte(self):
        response = self.fetch(
            '/api/v1/library/folders',
            method='POST',
            headers={'Content-Type': 'application/json'},
            body=b' ' * (MAX_MESSAGE_SIZE + 1),
            raise_error=False,
        )

        assert response.code == 413
        assert json.loads(response.body)['error']['code'] == 'request_too_large'

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
