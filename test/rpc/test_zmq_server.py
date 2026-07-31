import json
import socket
import threading

import zmq

from jukebox.rpc import processor
from jukebox.rpc import server as rpc_server
from jukebox.rpc.client import RpcClient


def test_tcp_rpc_wire_format_and_malformed_json_recovery(monkeypatch):
    port_socket = socket.socket()
    port_socket.bind(('127.0.0.1', 0))
    port = port_socket.getsockname()[1]
    port_socket.close()

    monkeypatch.setattr(
        rpc_server.cfg,
        'getn',
        lambda *keys, default=None: port if keys == ('rpc', 'tcp_port') else default,
    )
    monkeypatch.setattr(
        processor.plugs,
        'call',
        lambda package, plugin, method, **kwargs: {
            'package': package,
            'plugin': plugin,
            'method': method,
            'kwargs': kwargs['kwargs'],
        },
    )

    context = zmq.Context()
    ready = threading.Event()
    holder = {}

    def run_server():
        server = rpc_server.RpcServer(context=context)
        holder['server'] = server
        ready.set()
        server.run()
        server.socket.close(0)

    thread = threading.Thread(target=run_server)
    thread.start()
    assert ready.wait(2)

    client = context.socket(zmq.REQ)
    client.setsockopt(zmq.RCVTIMEO, 2000)
    client.connect(f'tcp://127.0.0.1:{port}')
    try:
        client.send(b'{')
        malformed = json.loads(client.recv())
        assert malformed['error']['code'] == -1
        assert malformed['error']['message'].startswith('Malformed JSON:')

        client.send_json({
            'package': 'player',
            'plugin': 'ctrl',
            'method': 'status',
            'kwargs': {'verbose': True},
            'id': 'request-id',
        })
        assert client.recv_json() == {
            'result': {
                'package': 'player',
                'plugin': 'ctrl',
                'method': 'status',
                'kwargs': {'verbose': True},
            },
            'id': 'request-id',
        }

        python_client = RpcClient(f'tcp://127.0.0.1:{port}', context=context)
        assert python_client.enque(
            'player',
            'ctrl',
            'status',
            kwargs={'verbose': False},
        ) == {
            'package': 'player',
            'plugin': 'ctrl',
            'method': 'status',
            'kwargs': {'verbose': False},
        }
        python_client.queue.close(0)

        holder['server'].terminate()
        client.send_json({'package': 'player', 'plugin': 'ctrl'})
        client.recv_json()
        thread.join(2)
        assert not thread.is_alive()
    finally:
        client.close(0)
        if thread.is_alive():
            holder['server'].terminate()
        context.term()
