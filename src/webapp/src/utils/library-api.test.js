import {
  createLibraryFolder,
  deleteLibraryEntries,
  listLibraryEntries,
  refreshLibrary,
  uploadLibraryFile,
} from './library-api';

const jsonResponse = (body, options = {}) => ({
  json: jest.fn().mockResolvedValue(body),
  ok: options.ok ?? true,
  status: options.status ?? 200,
});

class FakeEventTarget {
  constructor() {
    this.listeners = {};
  }

  addEventListener(name, callback) {
    this.listeners[name] = callback;
  }

  emit(name, event = {}) {
    this.listeners[name]?.(event);
  }
}

class FakeXMLHttpRequest extends FakeEventTarget {
  static instances = [];

  constructor() {
    super();
    this.headers = {};
    this.status = 0;
    this.responseText = '';
    this.upload = new FakeEventTarget();
    FakeXMLHttpRequest.instances.push(this);
  }

  open(method, url) {
    this.method = method;
    this.url = url;
  }

  setRequestHeader(name, value) {
    this.headers[name] = value;
  }

  send(body) {
    this.body = body;
  }

  abort() {
    this.emit('abort');
  }

  respond(status, body) {
    this.status = status;
    this.responseText = JSON.stringify(body);
    this.emit('load');
  }
}

describe('library JSON API', () => {
  beforeEach(() => {
    global.fetch = jest.fn();
  });

  afterEach(() => {
    delete global.fetch;
  });

  test('creates folders, deletes entries, and refreshes MPD', async () => {
    fetch
      .mockResolvedValueOnce(jsonResponse({ entries: [{ name: 'track.mp3' }] }))
      .mockResolvedValueOnce(jsonResponse({ path: 'Album' }, { status: 201 }))
      .mockResolvedValueOnce(jsonResponse({ deleted: ['Album'] }))
      .mockResolvedValueOnce(jsonResponse({ update_id: '1' }));

    await expect(listLibraryEntries('My Album')).resolves.toEqual([{ name: 'track.mp3' }]);
    await expect(createLibraryFolder('.', 'Album')).resolves.toEqual({ path: 'Album' });
    await expect(deleteLibraryEntries(['Album'])).resolves.toEqual({ deleted: ['Album'] });
    await expect(refreshLibrary()).resolves.toEqual({ update_id: '1' });

    expect(fetch.mock.calls).toEqual([
      ['/api/v1/library/entries?folder=My+Album', expect.objectContaining({
        headers: { 'Content-Type': 'application/json' },
      })],
      ['/api/v1/library/folders', expect.objectContaining({
        body: JSON.stringify({ parent: '.', name: 'Album' }),
        method: 'POST',
      })],
      ['/api/v1/library/entries', expect.objectContaining({
        body: JSON.stringify({ paths: ['Album'] }),
        method: 'DELETE',
      })],
      ['/api/v1/library/refresh', expect.objectContaining({
        method: 'POST',
      })],
    ]);
  });

  test('returns structured API errors', async () => {
    fetch.mockResolvedValue(jsonResponse(
      { error: { code: 'duplicate_name', message: 'Already exists.' } },
      { ok: false, status: 409 },
    ));

    await expect(createLibraryFolder('.', 'Album')).rejects.toMatchObject({
      code: 'duplicate_name',
      message: 'Already exists.',
      status: 409,
    });
  });
});

describe('streaming library upload', () => {
  beforeEach(() => {
    FakeXMLHttpRequest.instances = [];
    global.XMLHttpRequest = FakeXMLHttpRequest;
  });

  afterEach(() => {
    delete global.XMLHttpRequest;
  });

  test('sends a raw file and reports progress', async () => {
    const file = new File(['audio'], 'track name.mp3', { type: 'audio/mpeg' });
    const onProgress = jest.fn();
    const result = uploadLibraryFile({
      file,
      folder: 'My Album',
      onProgress,
    });
    const request = FakeXMLHttpRequest.instances[0];

    expect(request.method).toBe('PUT');
    expect(request.url).toContain('folder=My+Album');
    expect(request.url).toContain('name=track+name.mp3');
    expect(request.headers['Content-Type']).toBe('audio/mpeg');
    expect(request.body).toBe(file);

    request.upload.emit('progress', {
      lengthComputable: true,
      loaded: 5,
      total: 10,
    });
    request.respond(201, { path: 'My Album/track name.mp3', size: 5 });

    await expect(result).resolves.toEqual({
      path: 'My Album/track name.mp3',
      size: 5,
    });
    expect(onProgress).toHaveBeenNthCalledWith(1, 50);
    expect(onProgress).toHaveBeenLastCalledWith(100);
  });

  test('aborts an active upload', async () => {
    const controller = new AbortController();
    const result = uploadLibraryFile({
      file: new File(['audio'], 'track.mp3'),
      folder: '.',
      signal: controller.signal,
    });

    controller.abort();

    await expect(result).rejects.toMatchObject({ code: 'cancelled' });
  });
});
