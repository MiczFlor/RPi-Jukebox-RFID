import { initSockets, socketRequest } from './index';

jest.mock('uuid', () => ({
  v4: () => 'request-id',
}));

class FakeWebSocket {
  static instances = [];

  constructor(url) {
    this.url = url;
    this.readyState = 0;
    this.sent = [];
    FakeWebSocket.instances.push(this);
  }

  open() {
    this.readyState = 1;
    this.onopen();
  }

  message(message) {
    this.onmessage({ data: JSON.stringify(message) });
  }

  send(message) {
    this.sent.push(JSON.parse(message));
  }

  close() {
    this.readyState = 3;
    if (this.onclose) {
      this.onclose();
    }
  }
}

const rpcResponse = (body, options = {}) => ({
  ok: options.ok ?? true,
  status: options.status ?? 200,
  text: jest.fn().mockResolvedValue(JSON.stringify(body)),
});

describe('socketRequest', () => {
  beforeEach(() => {
    global.fetch = jest.fn();
  });

  afterEach(() => {
    jest.useRealTimers();
    delete global.fetch;
  });

  test('posts RPC requests and returns the result', async () => {
    fetch.mockResolvedValue(rpcResponse({
      id: 'request-id',
      result: 12,
    }));

    await expect(
      socketRequest('volume', 'ctrl', 'get_volume', { channel: 1 })
    ).resolves.toBe(12);

    expect(fetch).toHaveBeenCalledWith('/api/v1/rpc', expect.objectContaining({
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    }));
    expect(JSON.parse(fetch.mock.calls[0][1].body)).toEqual({
      id: 'request-id',
      package: 'volume',
      plugin: 'ctrl',
      method: 'get_volume',
      kwargs: { channel: 1 },
    });
  });

  test('returns RPC and HTTP errors', async () => {
    fetch.mockResolvedValueOnce(rpcResponse({
      id: 'request-id',
      error: { message: 'plugin failed' },
    }));
    await expect(socketRequest('p', 'f', null, {})).rejects.toBe('plugin failed');

    fetch.mockResolvedValueOnce(rpcResponse(
      { error: 'bad request' },
      { ok: false, status: 400 },
    ));
    await expect(socketRequest('p', 'f', null, {}))
      .rejects.toBe('RPC request failed with HTTP 400.');
  });

  test('rejects mismatched response IDs', async () => {
    fetch.mockResolvedValue(rpcResponse({
      id: 'different-id',
      result: null,
    }));

    await expect(socketRequest('p', 'f', null, {}))
      .rejects.toBe('Received RPC response ID does not match sender ID.');
  });

  test('aborts requests after 15 seconds', async () => {
    jest.useFakeTimers();
    fetch.mockImplementation((url, { signal }) => (
      new Promise((resolve, reject) => {
        signal.addEventListener('abort', () => {
          const error = new Error('aborted');
          error.name = 'AbortError';
          reject(error);
        });
      })
    ));

    const request = socketRequest('p', 'f', null, {});
    jest.advanceTimersByTime(15000);

    await expect(request).rejects.toBe('Request timed out');
  });
});

describe('initSockets', () => {
  beforeEach(() => {
    jest.useFakeTimers();
    FakeWebSocket.instances = [];
    global.WebSocket = FakeWebSocket;
  });

  afterEach(() => {
    jest.useRealTimers();
    delete global.WebSocket;
  });

  test('subscribes, decodes events, and applies revocations', () => {
    let state = {};
    const setState = updater => {
      state = updater(state);
    };
    const cleanup = initSockets({
      events: ['player'],
      setState,
    });
    const socket = FakeWebSocket.instances[0];

    expect(socket.url).toBe('ws://localhost/api/v1/events');
    socket.open();
    expect(socket.sent).toEqual([{
      type: 'subscribe',
      topics: ['player'],
    }]);

    socket.message({
      type: 'event',
      topic: 'player.status',
      data: false,
    });
    expect(state).toEqual({ 'player.status': false });

    socket.message({
      type: 'revoke',
      topic: 'player.status',
    });
    expect(state).toEqual({});

    cleanup();
    expect(socket.sent[1]).toEqual({
      type: 'unsubscribe',
      topics: ['player'],
    });
  });

  test('reconnects with exponential delay and resubscribes', () => {
    const cleanup = initSockets({
      events: ['core', 'volume'],
      setState: jest.fn(),
    });
    const first = FakeWebSocket.instances[0];
    first.open();
    first.close();

    jest.advanceTimersByTime(999);
    expect(FakeWebSocket.instances).toHaveLength(1);
    jest.advanceTimersByTime(1);
    expect(FakeWebSocket.instances).toHaveLength(2);

    const second = FakeWebSocket.instances[1];
    second.open();
    expect(second.sent).toEqual([{
      type: 'subscribe',
      topics: ['core', 'volume'],
    }]);

    cleanup();
  });
});
