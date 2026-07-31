import importlib.util
import json
import time
from pathlib import Path

import zmq

SUBSCRIBER_PATH = (
    Path(__file__).parents[2]
    / 'src'
    / 'jukebox'
    / 'jukebox'
    / 'publishing'
    / 'subscriber.py'
)
SPEC = importlib.util.spec_from_file_location('subscriber_under_test', SUBSCRIBER_PATH)
subscriber_module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(subscriber_module)
Subscriber = subscriber_module.Subscriber


def test_tcp_subscriber_wire_format():
    context = zmq.Context.instance()
    publisher = context.socket(zmq.PUB)
    port = publisher.bind_to_random_port('tcp://127.0.0.1')
    subscriber = Subscriber(
        f'tcp://127.0.0.1:{port}',
        topics=['core'],
    )
    subscriber.socket.setsockopt(zmq.RCVTIMEO, 1000)

    try:
        deadline = time.monotonic() + 2
        received = None
        while received is None and time.monotonic() < deadline:
            publisher.send_multipart([
                b'core.version',
                json.dumps('test-version').encode('utf-8'),
            ])
            try:
                received = subscriber.receive()
            except zmq.Again:
                pass

        assert received == ['core.version', 'test-version']
    finally:
        subscriber.socket.close(0)
        publisher.close(0)
