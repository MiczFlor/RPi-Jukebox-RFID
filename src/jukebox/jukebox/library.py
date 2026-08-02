# -*- coding: utf-8 -*-
"""Safe file operations within the configured MPD music library."""

import errno
import os
import shutil
import tempfile
from pathlib import Path, PurePosixPath


MAX_UPLOAD_SIZE = 1024 * 1024 * 1024
MAX_DELETE_ENTRIES = 1000

AUDIO_EXTENSIONS = frozenset({
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
})
PLAYLIST_EXTENSIONS = frozenset({'.m3u', '.m3u8', '.pls'})
COVER_EXTENSIONS = frozenset({'.gif', '.jpeg', '.jpg', '.png', '.webp'})
TEXT_FILE_ENDINGS = ('livestream.txt', 'podcast.txt')
SUPPORTED_EXTENSIONS = AUDIO_EXTENSIONS | PLAYLIST_EXTENSIONS | COVER_EXTENSIONS


class LibraryError(Exception):
    """An expected library operation failure suitable for an HTTP response."""

    def __init__(self, status, code, message):
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message


def _contains_path(root, path):
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _parse_relative_path(value, *, allow_root):
    if not isinstance(value, str):
        raise LibraryError(400, 'invalid_path', 'The library path must be a string.')
    if '\x00' in value or '\\' in value:
        raise LibraryError(400, 'invalid_path', 'The library path contains invalid characters.')

    path = PurePosixPath(value)
    if path.is_absolute() or '..' in path.parts:
        raise LibraryError(400, 'invalid_path', 'The library path must stay within the music library.')

    parts = tuple(part for part in path.parts if part != '.')
    if not allow_root and not parts:
        raise LibraryError(400, 'invalid_path', 'The music-library root cannot be selected.')
    return parts


def resolve_library_path(root, value, *, allow_root=True, require_exists=False):
    """Resolve a relative or internal absolute path without escaping ``root``."""
    root = Path(root).expanduser().resolve(strict=True)
    candidate = Path(value).expanduser()
    if not candidate.is_absolute():
        parts = _parse_relative_path(str(value), allow_root=allow_root)
        candidate = root.joinpath(*parts)

    resolved = candidate.resolve(strict=require_exists)
    if not _contains_path(root, resolved) or (not allow_root and resolved == root):
        raise LibraryError(400, 'invalid_path', 'The library path must stay within the music library.')
    return resolved


def _validate_name(name, *, file_name=False):
    if (
        not isinstance(name, str)
        or not name
        or name in ('.', '..')
        or name.startswith('.')
        or '/' in name
        or '\\' in name
        or '\x00' in name
    ):
        kind = 'file' if file_name else 'folder'
        raise LibraryError(400, f'invalid_{kind}_name', f'The {kind} name is invalid.')
    return name


def _validate_file_type(name):
    lower_name = name.casefold()
    if lower_name.endswith(TEXT_FILE_ENDINGS):
        return
    if Path(lower_name).suffix not in SUPPORTED_EXTENSIONS:
        raise LibraryError(415, 'unsupported_file_type', f"'{name}' is not a supported library file.")


def _entry_type(name):
    lower_name = name.casefold()
    suffix = Path(lower_name).suffix
    if lower_name.endswith('livestream.txt'):
        return 'stream'
    if lower_name.endswith('podcast.txt'):
        return 'podcast'
    if suffix in AUDIO_EXTENSIONS:
        return 'file'
    if suffix in PLAYLIST_EXTENSIONS:
        return 'playlist'
    if suffix in COVER_EXTENSIONS:
        return 'image'
    return 'other'


def _operation_error(error, action):
    if error.errno in (errno.ENOSPC, errno.EDQUOT):
        return LibraryError(507, 'insufficient_storage', f'Not enough storage to {action}.')
    if error.errno in (errno.EACCES, errno.EPERM, errno.EROFS):
        return LibraryError(403, 'permission_denied', f'Permission denied while trying to {action}.')
    return LibraryError(500, 'storage_error', f'Could not {action}: {error.strerror or error}.')


class UploadSession:
    """Write one upload to a temporary file and publish it atomically."""

    def __init__(self, target, reservation_fd, temporary_path, stream):
        self.target = target
        self.relative_path = None
        self._reservation_fd = reservation_fd
        reservation = os.fstat(reservation_fd)
        self._reservation_identity = (reservation.st_dev, reservation.st_ino)
        self._temporary_path = temporary_path
        self._stream = stream
        self.size = 0
        self._completed = False

    def write(self, chunk):
        if self.size + len(chunk) > MAX_UPLOAD_SIZE:
            raise LibraryError(413, 'file_too_large', 'Files are limited to 1 GiB.')
        try:
            self._stream.write(chunk)
            self.size += len(chunk)
        except OSError as error:
            raise _operation_error(error, f"write '{self.target.name}'") from error

    def finish(self):
        try:
            self._stream.flush()
            os.fsync(self._stream.fileno())
            self._stream.close()
            self._stream = None

            current = os.stat(self.target, follow_symlinks=False)
            current_identity = (current.st_dev, current.st_ino)
            if current_identity != self._reservation_identity:
                raise LibraryError(
                    409,
                    'duplicate_name',
                    f"'{self.target.name}' was created while the upload was running.",
                )

            os.chmod(self._temporary_path, 0o666)
            os.replace(self._temporary_path, self.target)
            self._temporary_path = None
            self._completed = True
        except LibraryError:
            self.abort()
            raise
        except OSError as error:
            self.abort()
            raise _operation_error(error, f"save '{self.target.name}'") from error
        finally:
            self._close_reservation()

    def abort(self):
        if self._stream is not None:
            try:
                self._stream.close()
            except OSError:
                pass
            self._stream = None

        if self._temporary_path is not None:
            try:
                self._temporary_path.unlink(missing_ok=True)
            except OSError:
                pass
            self._temporary_path = None

        if not self._completed:
            try:
                current = os.stat(self.target, follow_symlinks=False)
                current_identity = (current.st_dev, current.st_ino)
                if current_identity == self._reservation_identity:
                    self.target.unlink()
            except (FileNotFoundError, OSError):
                pass
        self._close_reservation()

    def _close_reservation(self):
        if self._reservation_fd is not None:
            try:
                os.close(self._reservation_fd)
            except OSError:
                pass
            self._reservation_fd = None


class MusicLibrary:
    """Perform validated mutations beneath a lazily resolved library root."""

    def __init__(self, root_provider, update_callback):
        self._root_provider = root_provider
        self._update_callback = update_callback

    @property
    def root(self):
        root_value = self._root_provider()
        if not root_value:
            raise LibraryError(503, 'library_unavailable', 'The MPD music-library path is unavailable.')
        try:
            root = Path(root_value).expanduser().resolve(strict=True)
        except (OSError, RuntimeError) as error:
            raise LibraryError(503, 'library_unavailable', 'The MPD music-library path is unavailable.') from error
        if not root.is_dir():
            raise LibraryError(503, 'library_unavailable', 'The MPD music-library path is not a directory.')
        return root

    def _directory(self, relative_path):
        parts = _parse_relative_path(relative_path, allow_root=True)
        candidate = self.root.joinpath(*parts)
        try:
            resolved = candidate.resolve(strict=True)
        except FileNotFoundError as error:
            raise LibraryError(404, 'folder_not_found', 'The destination folder does not exist.') from error
        if not _contains_path(self.root, resolved):
            raise LibraryError(400, 'invalid_path', 'The library path must stay within the music library.')
        if not resolved.is_dir():
            raise LibraryError(400, 'not_a_folder', 'The destination path is not a folder.')
        return resolved

    def start_upload(self, folder, file_name):
        file_name = _validate_name(file_name, file_name=True)
        _validate_file_type(file_name)
        parent = self._directory(folder)
        target = parent / file_name

        try:
            reservation_fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o666)
        except FileExistsError as error:
            raise LibraryError(
                409,
                'duplicate_name',
                f"'{file_name}' already exists in this folder.",
            ) from error
        except OSError as error:
            raise _operation_error(error, f"reserve '{file_name}'") from error

        temporary_path = None
        try:
            temporary_fd, temporary_name = tempfile.mkstemp(
                prefix='.phoniebox-upload-',
                suffix='.part',
                dir=parent,
            )
            temporary_path = Path(temporary_name)
            stream = os.fdopen(temporary_fd, 'wb')
            session = UploadSession(target, reservation_fd, temporary_path, stream)
            session.relative_path = target.relative_to(self.root).as_posix()
            return session
        except OSError as error:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)
            reservation = os.fstat(reservation_fd)
            reservation_identity = (reservation.st_dev, reservation.st_ino)
            try:
                current = os.stat(target, follow_symlinks=False)
                if (current.st_dev, current.st_ino) == reservation_identity:
                    target.unlink()
            except OSError:
                pass
            finally:
                os.close(reservation_fd)
            raise _operation_error(error, f"start upload for '{file_name}'") from error

    def create_folder(self, parent, name):
        name = _validate_name(name)
        target = self._directory(parent) / name
        try:
            target.mkdir(mode=0o777)
            target.chmod(0o777)
        except FileExistsError as error:
            raise LibraryError(
                409,
                'duplicate_name',
                f"'{name}' already exists in this folder.",
            ) from error
        except OSError as error:
            raise _operation_error(error, f"create folder '{name}'") from error
        return target.relative_to(self.root).as_posix()

    def list_entries(self, folder):
        root = self.root
        parent = self._directory(folder)
        entries = []
        try:
            directory_entries = sorted(
                os.scandir(parent),
                key=lambda entry: (not entry.is_dir(follow_symlinks=True), entry.name.casefold()),
            )
            for entry in directory_entries:
                if entry.name.startswith('.'):
                    continue
                resolved = Path(entry.path).resolve(strict=False)
                if not _contains_path(root, resolved):
                    continue
                if entry.is_dir(follow_symlinks=True):
                    entry_type = 'directory'
                elif entry.is_file(follow_symlinks=True):
                    entry_type = _entry_type(entry.name)
                else:
                    continue
                entries.append({
                    'name': entry.name,
                    'relpath': Path(entry.path).relative_to(root).as_posix(),
                    'type': entry_type,
                })
        except OSError as error:
            raise _operation_error(error, f"list folder '{folder}'") from error
        return entries

    def delete_entries(self, relative_paths):
        if not isinstance(relative_paths, list) or not relative_paths:
            raise LibraryError(400, 'invalid_request', 'Select at least one file or folder to delete.')
        if len(relative_paths) > MAX_DELETE_ENTRIES:
            raise LibraryError(
                400,
                'too_many_entries',
                f'At most {MAX_DELETE_ENTRIES} entries can be deleted at once.',
            )

        root = self.root
        targets = {}
        for relative_path in relative_paths:
            parts = _parse_relative_path(relative_path, allow_root=False)
            candidate = root.joinpath(*parts)
            try:
                candidate.lstat()
            except FileNotFoundError as error:
                raise LibraryError(404, 'entry_not_found', f"'{relative_path}' does not exist.") from error

            resolved = candidate.resolve(strict=False)
            if not _contains_path(root, resolved):
                raise LibraryError(400, 'invalid_path', 'The library path must stay within the music library.')
            targets[candidate] = relative_path

        deleted = []
        for target in sorted(targets, key=lambda path: len(path.parts), reverse=True):
            try:
                if target.is_symlink() or not target.is_dir():
                    target.unlink()
                else:
                    shutil.rmtree(target)
            except FileNotFoundError:
                continue
            except OSError as error:
                raise _operation_error(error, f"delete '{targets[target]}'") from error
            deleted.append(targets[target])
        return deleted

    def update(self):
        try:
            return self._update_callback()
        except Exception as error:
            raise LibraryError(502, 'mpd_update_failed', f'Could not update the MPD library: {error}') from error


def create_music_library():
    """Create the production library service after player plugins are loaded."""
    import components.player
    import jukebox.plugs

    return MusicLibrary(
        components.player.get_music_library_path,
        lambda: jukebox.plugs.call('player', 'ctrl', 'update'),
    )
