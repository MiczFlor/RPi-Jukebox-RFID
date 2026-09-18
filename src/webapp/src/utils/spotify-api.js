const SPOTIFY_ENDPOINT = '/api/v1/spotify';

class SpotifyApiError extends Error {
  constructor(code, message, status = 0) {
    super(message);
    this.name = 'SpotifyApiError';
    this.code = code;
    this.status = status;
  }
}

const spotifyRequest = async (path = '', options = {}) => {
  const response = await fetch(`${SPOTIFY_ENDPOINT}${path}`, options);
  let data = {};
  if (response.status !== 204) {
    try {
      data = await response.json();
    }
    catch {
      // The generic response below covers invalid error bodies.
    }
  }
  if (!response.ok) {
    throw new SpotifyApiError(
      data?.error?.code || 'request_failed',
      data?.error?.message || `Request failed with status ${response.status}.`,
      response.status,
    );
  }
  return data;
};

const getSpotifyStatus = () => spotifyRequest();

const startSpotifyAuthorization = () => spotifyRequest('/oauth/start', {
  method: 'POST',
});

const disconnectSpotify = () => spotifyRequest('', {
  method: 'DELETE',
});

const getSpotifyLibrary = () => spotifyRequest('/library');

const setSpotifyLibraryMode = (mode) => spotifyRequest('/library', {
  method: 'PUT',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ mode }),
});

const addSpotifyLibraryItem = (link) => spotifyRequest('/library/items', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ link }),
});

const removeSpotifyLibraryItem = (uri) => spotifyRequest('/library/items', {
  method: 'DELETE',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ uri }),
});

const removeSpotifyLibraryItems = (uris) => spotifyRequest('/library/items', {
  method: 'DELETE',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ uris }),
});

export {
  SpotifyApiError,
  addSpotifyLibraryItem,
  disconnectSpotify,
  getSpotifyLibrary,
  getSpotifyStatus,
  removeSpotifyLibraryItem,
  removeSpotifyLibraryItems,
  setSpotifyLibraryMode,
  startSpotifyAuthorization,
};
