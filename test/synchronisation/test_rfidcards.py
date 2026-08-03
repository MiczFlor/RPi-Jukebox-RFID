import importlib
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

import jukebox.plugs as plugin


def _passthrough_decorator(obj=None, **ignored_kwargs):
    if obj is None:
        return lambda decorated: decorated
    return obj


@pytest.fixture
def rfidcards(monkeypatch):
    monkeypatch.setattr(plugin, 'register', _passthrough_decorator)
    monkeypatch.setattr(plugin, 'initialize', _passthrough_decorator)
    monkeypatch.setattr(plugin, 'finalize', _passthrough_decorator)
    monkeypatch.setattr(plugin, 'atexit', _passthrough_decorator)
    monkeypatch.setattr(plugin, 'tag', _passthrough_decorator)

    sys.modules.pop('components.synchronisation.rfidcards', None)
    module = importlib.import_module('components.synchronisation.rfidcards')
    yield module
    sys.modules.pop('components.synchronisation.rfidcards', None)


def test_sync_paths_builds_mount_mode_rsync_command(rfidcards, monkeypatch):
    run = MagicMock(return_value=SimpleNamespace(
        returncode=0,
        stdout='',
        stderr='',
    ))
    monkeypatch.setattr(rfidcards.subprocess, 'run', run)
    controller = rfidcards.SyncRfidcards.__new__(rfidcards.SyncRfidcards)
    controller._sync_is_mode_ssh = False

    assert controller._sync_paths('/media/source', '/media/destination') is False

    run.assert_called_once_with(
        [
            'rsync',
            '--recursive', '--itemize-changes',
            '--safe-links', '--times', '--omit-dir-times',
            '--delete', '--prune-empty-dirs',
            '--exclude=folder.conf',
            '--exclude=.*', '--exclude=.*/', '--exclude=@*/', '--cvs-exclude',
            '/media/source', '/media/destination',
        ],
        shell=False,
        check=False,
        capture_output=True,
        text=True,
    )


@pytest.mark.parametrize('source_path', [
    '/srv/audiofolders/album',
    '/srv/audiofolders/favorite album',
])
def test_sync_paths_protects_ssh_source_path(
        rfidcards, monkeypatch, source_path):
    run = MagicMock(return_value=SimpleNamespace(
        returncode=0,
        stdout='',
        stderr='',
    ))
    monkeypatch.setattr(rfidcards.subprocess, 'run', run)
    controller = rfidcards.SyncRfidcards.__new__(rfidcards.SyncRfidcards)
    controller._sync_is_mode_ssh = True
    controller._sync_remote_ssh_user = 'jukebox'
    controller._sync_remote_server = 'music.example.com'
    controller._sync_remote_port = 2222

    assert controller._sync_paths(source_path, '/media/destination') is False

    run.assert_called_once_with(
        [
            'rsync',
            '--recursive', '--itemize-changes',
            '--safe-links', '--times', '--omit-dir-times',
            '--delete', '--prune-empty-dirs',
            '--exclude=folder.conf',
            '--exclude=.*', '--exclude=.*/', '--exclude=@*/', '--cvs-exclude',
            '--compress', '--protect-args', '-e', 'ssh -p 2222',
            f'jukebox@music.example.com:{source_path}', '/media/destination',
        ],
        shell=False,
        check=False,
        capture_output=True,
        text=True,
    )
