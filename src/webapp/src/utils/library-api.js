const LIBRARY_ENDPOINT = '/api/v1/library';

const ACCEPTED_LIBRARY_FILES = [
  '.aac',
  '.aif',
  '.aiff',
  '.ape',
  '.flac',
  '.m4a',
  '.m4b',
  '.mp3',
  '.mp4',
  '.oga',
  '.ogg',
  '.opus',
  '.wav',
  '.wma',
  '.wv',
  '.m3u',
  '.m3u8',
  '.pls',
  '.gif',
  '.jpeg',
  '.jpg',
  '.png',
  '.webp',
  '.txt',
].join(',');

class LibraryApiError extends Error {
  constructor(code, message, status = 0) {
    super(message);
    this.name = 'LibraryApiError';
    this.code = code;
    this.status = status;
  }
}

const responseData = async (response) => {
  let data = {};
  try {
    data = await response.json();
  }
  catch {
    if (response.ok) return data;
  }

  if (!response.ok) {
    throw new LibraryApiError(
      data?.error?.code || 'request_failed',
      data?.error?.message || `Request failed with status ${response.status}.`,
      response.status,
    );
  }
  return data;
};

const jsonRequest = async (path, options = {}) => {
  const response = await fetch(`${LIBRARY_ENDPOINT}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });
  return responseData(response);
};

const createLibraryFolder = (parent, name, options = {}) => jsonRequest('/folders', {
  method: 'POST',
  body: JSON.stringify({ parent, name }),
  signal: options.signal,
});

const listLibraryEntries = async (folder) => {
  const query = new URLSearchParams({ folder });
  const data = await jsonRequest(`/entries?${query.toString()}`);
  return data.entries;
};

const deleteLibraryEntries = (paths) => jsonRequest('/entries', {
  method: 'DELETE',
  body: JSON.stringify({ paths }),
});

const refreshLibrary = () => jsonRequest('/refresh', {
  method: 'POST',
  body: '',
});

const uploadLibraryFile = ({
  folder,
  file,
  onProgress = () => {},
  signal,
}) => new Promise((resolve, reject) => {
  const query = new URLSearchParams({ folder, name: file.name });
  const request = new XMLHttpRequest();

  const fail = (code, message, status = request.status) => {
    reject(new LibraryApiError(code, message, status));
  };

  const abort = () => request.abort();
  if (signal?.aborted) {
    fail('cancelled', 'Upload cancelled.');
    return;
  }
  signal?.addEventListener('abort', abort, { once: true });

  request.open('PUT', `${LIBRARY_ENDPOINT}/files?${query.toString()}`);
  request.setRequestHeader('Content-Type', file.type || 'application/octet-stream');
  request.upload.addEventListener('progress', (event) => {
    if (event.lengthComputable) {
      onProgress(Math.round((event.loaded / event.total) * 100));
    }
  });
  request.addEventListener('load', () => {
    signal?.removeEventListener('abort', abort);
    let data = {};
    try {
      data = JSON.parse(request.responseText || '{}');
    }
    catch {
      // The status and generic message below still describe invalid responses.
    }
    if (request.status >= 200 && request.status < 300) {
      onProgress(100);
      resolve(data);
      return;
    }
    fail(
      data?.error?.code || 'request_failed',
      data?.error?.message || `Upload failed with status ${request.status}.`,
    );
  });
  request.addEventListener('error', () => {
    signal?.removeEventListener('abort', abort);
    fail('network_error', 'The upload connection failed.');
  });
  request.addEventListener('abort', () => {
    signal?.removeEventListener('abort', abort);
    fail('cancelled', 'Upload cancelled.');
  });
  request.send(file);
});

const translateLibraryError = (t, error) => t(
  `library.folders.manager.errors.${error.code}`,
  { defaultValue: error.message },
);

export {
  ACCEPTED_LIBRARY_FILES,
  LibraryApiError,
  createLibraryFolder,
  deleteLibraryEntries,
  listLibraryEntries,
  refreshLibrary,
  translateLibraryError,
  uploadLibraryFile,
};
