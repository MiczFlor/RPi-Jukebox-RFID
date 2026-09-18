"""Persistent storage for the Jellyfin login token and the device id.

The token is kept so that a daemon restart does not replace the device and the
session on the server: Jellyfin logs out every device of the same user with the
same device id on login, and the stream URLs that MPD still holds in its queue
keep a valid token. The file also records which user and which device id the
token was issued for, so a token from a different identity is never reused. The
per-installation device id lives here as well, because Jellyfin keys devices by
(DeviceId, user).
"""

import json
import logging
import os
import tempfile
import threading
import uuid
from pathlib import Path


logger = logging.getLogger('jb.player.jellyfin')


class JellyfinTokenStore:
    """Read and write the login token and the device id with mode 0600.

    Writes go through a temporary file that is flushed, fsynced and renamed,
    so an interrupted write can never leave a truncated file behind. The
    pattern mirrors SpotifyJsonStore in components/player/spotify.py.

    The token is stored together with the user name and the device id it was
    issued for (``token_username`` and ``token_device_id``). Those two fields
    are written only by ``save()``; ``device_id`` is the installation's
    current id and may be rewritten by ``device_id()``, so it is no binding
    for a token.
    """

    def __init__(self, path):
        self.path = Path(path).expanduser()
        self._lock = threading.Lock()

    def load(self, username, device_id):
        """Return (token, user_id) for this identity, or (None, None).

        A token is returned only when it was issued for the same Jellyfin user
        and the same device id. Both belong to the identity the server binds
        the session to, and the server resolves a request by its token alone,
        so a token from a different identity would keep the box authenticated
        as the previous user or device. A mismatch leaves the file untouched;
        the next login overwrites the record.
        """
        with self._lock:
            payload = self._read()
        token = str(payload.get('access_token') or '')
        if not token:
            return None, None
        stored_user = str(payload.get('token_username') or '')
        stored_device = str(payload.get('token_device_id') or '')
        if (stored_user != str(username or '')
                or stored_device != str(device_id or '')):
            logger.info(
                "Stored Jellyfin token belongs to user '%s' and device '%s'; "
                "logging in for user '%s' on device '%s' instead",
                stored_user, stored_device, username, device_id)
            return None, None
        user_id = str(payload.get('user_id') or '')
        return token, (user_id or None)

    def save(self, token, user_id, username, device_id):
        """Store the token together with the identity it was issued for."""
        with self._lock:
            payload = self._read()
            payload['access_token'] = token
            payload['user_id'] = user_id or ''
            payload['token_username'] = username or ''
            payload['token_device_id'] = device_id or ''
            self._write(payload)

    def device_id(self, configured=''):
        """Return the device id for this installation, creating one on first use.

        Jellyfin keys devices by (DeviceId, user) and logs out every device
        with the same pair on login, so a shared constant would make two
        Phonieboxen that use the same Jellyfin user log each other out. A
        configured id wins and is persisted, so a cloned SD card image can be
        given its own identity in jukebox.yaml.

        The binding stored with an existing token (``token_device_id``) is left
        alone on purpose: a device id set here takes effect on the next login
        and discards a token that belongs to the previous device.
        """
        configured = str(configured or '').strip()
        with self._lock:
            payload = self._read()
            if configured:
                if payload.get('device_id') != configured:
                    payload['device_id'] = configured
                    self._write(payload)
                return configured
            device_id = str(payload.get('device_id') or '')
            if not device_id:
                device_id = uuid.uuid4().hex
                payload['device_id'] = device_id
                self._write(payload)
                logger.info(
                    "Generated Jellyfin device id '%s' and stored it in '%s'",
                    device_id, self.path)
            return device_id

    def clear(self):
        """Remove the stored token, e.g. after the server rejected it.

        The device id is kept: it identifies the installation, not the token.
        The identity the discarded token was issued for goes away with it.
        Raises OSError when the file cannot be written; callers treat that as
        a logged warning, because it only costs a second login after the next
        restart.
        """
        with self._lock:
            payload = self._read()
            if not payload:
                return
            payload.pop('access_token', None)
            payload.pop('user_id', None)
            payload.pop('token_username', None)
            payload.pop('token_device_id', None)
            self._write(payload)

    def _read(self):
        """Return the stored mapping; the caller holds the lock."""
        try:
            with self.path.open(encoding='utf-8') as stream:
                value = json.load(stream)
        except FileNotFoundError:
            return {}
        except (OSError, json.JSONDecodeError) as error:
            logger.warning(
                "Could not read Jellyfin token file '%s': %s", self.path, error)
            return {}
        return value if isinstance(value, dict) else {}

    def _write(self, payload):
        """Write payload atomically with mode 0600; the caller holds the lock."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary_name = tempfile.mkstemp(
            prefix='.' + self.path.name + '.', dir=self.path.parent)
        try:
            os.fchmod(descriptor, 0o600)
            with os.fdopen(descriptor, 'w', encoding='utf-8') as stream:
                json.dump(payload, stream)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary_name, self.path)
            os.chmod(self.path, 0o600)
        except Exception:
            try:
                os.close(descriptor)
            except OSError:
                pass
            try:
                os.unlink(temporary_name)
            except FileNotFoundError:
                pass
            raise
