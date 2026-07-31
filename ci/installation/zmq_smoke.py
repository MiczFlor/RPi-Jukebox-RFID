#!/usr/bin/env python3
"""Smoke-test the standard ZeroMQ transports used by Phoniebox."""

import time

import zmq


def main():
    context = zmq.Context()

    reply = context.socket(zmq.REP)
    port = reply.bind_to_random_port("tcp://127.0.0.1")
    request = context.socket(zmq.REQ)
    request.connect(f"tcp://127.0.0.1:{port}")
    request.send(b"request")
    assert reply.poll(1000), "TCP REP socket did not receive a request"
    assert reply.recv() == b"request"
    reply.send(b"response")
    assert request.poll(1000), "TCP REQ socket did not receive a response"
    assert request.recv() == b"response"
    request.close(0)
    reply.close(0)

    subscriber = context.socket(zmq.SUB)
    subscriber.setsockopt(zmq.SUBSCRIBE, b"")
    subscriber.bind("inproc://jukebox-install-smoke")
    publisher = context.socket(zmq.PUB)
    publisher.connect("inproc://jukebox-install-smoke")
    deadline = time.monotonic() + 2
    publication = None
    while publication is None and time.monotonic() < deadline:
        publisher.send_multipart([b"topic", b"payload"])
        if subscriber.poll(50):
            publication = subscriber.recv_multipart()
    assert publication == [b"topic", b"payload"], (
        "inproc SUB socket did not receive a publication"
    )
    publisher.close(0)
    subscriber.close(0)
    context.term()


if __name__ == '__main__':
    main()
