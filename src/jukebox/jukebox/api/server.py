# -*- coding: utf-8 -*-
"""Tornado HTTP RPC and WebSocket event server."""

import asyncio
import json
import logging
import threading
from concurrent.futures import ThreadPoolExecutor

import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.websocket
import zmq
from zmq.eventloop.zmqstream import ZMQStream

import jukebox.cfghandler
from jukebox.rpc.processor import process_request

logger = logging.getLogger('jb.api.server')
cfg = jukebox.cfghandler.get_handler('jukebox')

MAX_MESSAGE_SIZE = 1024 * 1024
PING_INTERVAL_SECONDS = 30
PING_TIMEOUT_SECONDS = 30
PUBLISH_ENDPOINT = 'inproc://PublisherToProxy'


class EventBroker:
    """Maintain browser subscriptions and a private last-value cache."""

    def __init__(self):
        self.cache = {}
        self.clients = set()

    def register(self, client):
        self.clients.add(client)

    def unregister(self, client):
        self.clients.discard(client)

    @staticmethod
    def _matches(topic, subscriptions):
        return any(topic.startswith(prefix) for prefix in subscriptions)

    def subscribe(self, client, topics):
        client.subscriptions.update(topics)
        for topic, data in self.cache.items():
            if self._matches(topic, topics):
                self._send(client, {
                    'type': 'event',
                    'topic': topic,
                    'data': data,
                })

    @staticmethod
    def unsubscribe(client, topics):
        client.subscriptions.difference_update(topics)

    def publish(self, message):
        if len(message) != 2:
            logger.warning(f"Ignoring malformed publisher message with {len(message)} parts")
            return

        topic_bytes, payload = message
        try:
            topic = topic_bytes.decode('utf-8')
        except UnicodeDecodeError as error:
            logger.warning(f"Ignoring publisher topic that is not UTF-8: {error}")
            return

        if payload == b'':
            self.cache.pop(topic, None)
            outgoing = {'type': 'revoke', 'topic': topic}
        else:
            try:
                data = json.loads(payload)
            except (json.JSONDecodeError, UnicodeDecodeError) as error:
                logger.warning(f"Ignoring malformed publisher payload for '{topic}': {error}")
                return
            self.cache[topic] = data
            outgoing = {'type': 'event', 'topic': topic, 'data': data}

        for client in tuple(self.clients):
            if self._matches(topic, client.subscriptions):
                self._send(client, outgoing)

    def _send(self, client, message):
        try:
            future = client.write_message(message)
        except tornado.websocket.WebSocketClosedError:
            self.unregister(client)
            return

        if future is not None:
            future.add_done_callback(lambda completed: completed.exception())


class HealthHandler(tornado.web.RequestHandler):
    def get(self):
        self.write({'status': 'ok'})


class RpcHandler(tornado.web.RequestHandler):
    def prepare(self):
        content_length = self.request.headers.get('Content-Length')
        if content_length is not None:
            try:
                too_large = int(content_length) > MAX_MESSAGE_SIZE
            except ValueError:
                too_large = False
            if too_large:
                self.set_status(413)
                self.finish({'error': 'Request body exceeds 1 MiB.'})

    async def post(self):
        if self._finished:
            return

        content_type = self.request.headers.get('Content-Type', '')
        media_type = content_type.split(';', 1)[0].strip().lower()
        if media_type != 'application/json':
            self.set_status(400)
            self.finish({'error': 'Content-Type must be application/json.'})
            return

        try:
            request = json.loads(self.request.body)
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            self.set_status(400)
            self.finish({'error': f'Malformed JSON: {error}'})
            return

        if not isinstance(request, dict):
            self.set_status(400)
            self.finish({'error': 'RPC request must be an object.'})
            return

        executor = self.settings['rpc_executor']
        processor = self.settings['rpc_processor']
        response = await tornado.ioloop.IOLoop.current().run_in_executor(
            executor,
            processor,
            request,
        )
        self.write(response)


class EventsHandler(tornado.websocket.WebSocketHandler):
    def initialize(self, broker):
        self.broker = broker
        self.subscriptions = set()

    def open(self):
        self.broker.register(self)

    def on_message(self, message):
        try:
            command = json.loads(message)
        except (json.JSONDecodeError, UnicodeDecodeError):
            self.close(code=1003, reason='Messages must contain JSON.')
            return

        if not isinstance(command, dict):
            self.close(code=1008, reason='Commands must be objects.')
            return

        command_type = command.get('type')
        topics = command.get('topics')
        if (
            command_type not in ('subscribe', 'unsubscribe')
            or not isinstance(topics, list)
            or any(not isinstance(topic, str) for topic in topics)
        ):
            self.close(code=1008, reason='Invalid subscription command.')
            return

        if command_type == 'subscribe':
            self.broker.subscribe(self, topics)
        else:
            self.broker.unsubscribe(self, topics)

    def on_close(self):
        self.broker.unregister(self)


def make_application(broker, executor, rpc_processor=process_request):
    return tornado.web.Application(
        [
            (r'/api/v1/health', HealthHandler),
            (r'/api/v1/rpc', RpcHandler),
            (r'/api/v1/events', EventsHandler, {'broker': broker}),
        ],
        rpc_executor=executor,
        rpc_processor=rpc_processor,
        websocket_max_message_size=MAX_MESSAGE_SIZE,
        websocket_ping_interval=PING_INTERVAL_SECONDS,
        websocket_ping_timeout=PING_TIMEOUT_SECONDS,
    )


class ApiServer(threading.Thread):
    """Run the browser API on an isolated Tornado I/O loop."""

    def __init__(self, bind_address=None, port=None, context=None):
        super().__init__(name='ApiServer', daemon=True)
        self.bind_address = bind_address or cfg.getn('api', 'bind_address', default='127.0.0.1')
        self.port = port if port is not None else cfg.getn('api', 'port', default=5556)
        self.context = context or zmq.Context.instance()
        self.broker = EventBroker()
        self._ready = threading.Event()
        self._startup_error = None
        self._io_loop = None
        self._http_server = None
        self._subscriber = None
        self._subscriber_stream = None
        self._executor = None
        self._stopping = False

    def start_and_wait(self, timeout=5):
        self.start()
        if not self._ready.wait(timeout):
            raise TimeoutError('Timed out while starting API server.')
        if self._startup_error is not None:
            raise RuntimeError('Could not start API server.') from self._startup_error

    def run(self):
        asyncio.set_event_loop(asyncio.new_event_loop())
        self._io_loop = tornado.ioloop.IOLoop.current()
        try:
            self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix='ApiRpc')
            application = make_application(self.broker, self._executor)
            self._http_server = tornado.httpserver.HTTPServer(
                application,
                max_body_size=MAX_MESSAGE_SIZE,
            )
            self._http_server.listen(self.port, address=self.bind_address)

            self._subscriber = self.context.socket(zmq.SUB)
            self._subscriber.setsockopt(zmq.SUBSCRIBE, b'')
            self._subscriber.setsockopt(zmq.LINGER, 0)
            self._subscriber.connect(PUBLISH_ENDPOINT)
            self._subscriber_stream = ZMQStream(self._subscriber, self._io_loop)
            self._subscriber_stream.on_recv(self.broker.publish)

            logger.info(f"API server listening on {self.bind_address}:{self.port}")
            self._ready.set()
            self._io_loop.start()
        except Exception as error:
            self._startup_error = error
            logger.exception("API server failed")
            self._ready.set()
        finally:
            self._close_resources()
            self._io_loop.close(all_fds=False)

    def terminate(self, timeout=5):
        logger.info("Closing API server")
        if not self.is_alive():
            return
        self._ready.wait(timeout)
        if self._io_loop is not None:
            self._io_loop.add_callback(self._stop_server)
        self.join(timeout)
        if self.is_alive():
            logger.warning("API server did not stop within the shutdown timeout")

    def _stop_server(self):
        if self._stopping:
            return
        self._stopping = True
        for client in tuple(self.broker.clients):
            client.close(code=1001, reason='Server shutting down.')
        if self._http_server is not None:
            self._http_server.stop()
        self._io_loop.stop()

    def _close_resources(self):
        if self._subscriber_stream is not None:
            self._subscriber_stream.close(linger=0)
            self._subscriber_stream = None
        elif self._subscriber is not None:
            self._subscriber.close(linger=0)
        self._subscriber = None

        if self._http_server is not None:
            self._http_server.stop()
            self._http_server = None

        if self._executor is not None:
            self._executor.shutdown(wait=False, cancel_futures=True)
            self._executor = None
