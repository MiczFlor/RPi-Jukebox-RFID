import json
import shutil
import subprocess
import threading
from pathlib import Path

import pytest
import zmq


HAS_CZMQ_HEADERS = any(
    path.exists()
    for path in (
        Path('/usr/include/czmq.h'),
        Path('/usr/local/include/czmq.h'),
    )
)


@pytest.mark.skipif(
    shutil.which('gcc') is None or not HAS_CZMQ_HEADERS,
    reason='gcc and libczmq-dev are required',
)
def test_c_client_tcp_wire_format(tmp_path):
    executable = tmp_path / 'pbc'
    subprocess.run(
        [
            'gcc',
            'src/cli_client/pbc.c',
            '-o',
            executable,
            '-lzmq',
            '-Wall',
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    context = zmq.Context()
    ready = threading.Event()
    received = {}

    def serve():
        socket = context.socket(zmq.REP)
        received['port'] = socket.bind_to_random_port('tcp://127.0.0.1')
        ready.set()
        received['request'] = json.loads(socket.recv())
        socket.send_json({'result': 'ok', 'id': 123})
        socket.close(0)

    server = threading.Thread(target=serve)
    server.start()
    assert ready.wait(2)

    result = subprocess.run(
        [
            executable,
            '-a',
            f"tcp://127.0.0.1:{received['port']}",
            '-p',
            'player',
            '-o',
            'ctrl',
            '-m',
            'status',
            'verbose:1',
        ],
        check=True,
        capture_output=True,
        text=True,
        timeout=5,
    )
    server.join(2)
    context.term()

    assert not server.is_alive()
    assert received['request'] == {
        'package': 'player',
        'plugin': 'ctrl',
        'method': 'status',
        'kwargs': {'verbose': 1},
        'id': 123,
    }
    assert 'Received {"result": "ok", "id": 123}' in result.stdout
