import sys
import os
sys.path.append(os.path.abspath('../../src/jukebox'))

import types  # noqa: E402
from unittest.mock import MagicMock  # noqa: E402

import pytest  # noqa: E402

# components.webui_plugins imports zmq (via zmq.eventloop.ioloop) at module level. Mock it out so
# these tests don't need a real pyzmq install -- same pattern as test/evdev/test_evdev_init.py uses
# for jukebox.publishing.
sys.modules.setdefault('zmq', MagicMock())
sys.modules.setdefault('zmq.eventloop', MagicMock())
sys.modules.setdefault('zmq.eventloop.ioloop', MagicMock())

import jukebox.plugs as plugs  # noqa: E402


def _register_fake_plugin(tmp_path, name, slot=None, entry=None, create_static_file=True):
    """Register a fake already-loaded plugin package, optionally declaring a UI extension"""
    module_dir = tmp_path / name
    module_dir.mkdir(parents=True, exist_ok=True)

    module = types.ModuleType(name)
    module.__file__ = str(module_dir / '__init__.py')
    if slot is not None:
        module.PLUGIN_UI_SLOT = slot
    if entry is not None:
        module.PLUGIN_UI_ENTRY = entry
        static_dir = module_dir / 'static'
        static_dir.mkdir(exist_ok=True)
        if create_static_file:
            (static_dir / entry).write_text('export function mount(){} export function unmount(){}')

    plugs._PLUGINS[name] = plugs.PluginPackageClass(name)
    plugs._PLUGINS[name].module = module


@pytest.fixture
def webui_plugins(monkeypatch):
    """Load components.webui_plugins fresh for each test, the same way the real daemon does
    (plugs.load(), not a plain import) -- this way the @plugin.finalize/@plugin.register decorators
    register correctly without needing the ALLOW_DIRECT_IMPORTS escape hatch, and each test gets an
    isolated module instance instead of a shared, import-cached one."""
    plugins_before = set(plugs._PLUGINS.keys())

    plugs.load('webui_plugins', prefix='components')
    module = plugs.get_module('webui_plugins')

    monkeypatch.setattr(module, '_server', None)
    # Never actually bind a socket / start a thread in these tests
    monkeypatch.setattr(module, '_UiExtensionServer', MagicMock())

    yield module

    # Clean up webui_plugins itself plus any fake plugins registered via _register_fake_plugin,
    # so nothing leaks into other tests (in this file or, since plugs' registries are process-global,
    # any other test file run in the same pytest session).
    for name in plugs._PLUGINS.keys() - plugins_before:
        del plugs._PLUGINS[name]
    del plugs._PACKAGE_MAP['components.webui_plugins']
    del sys.modules['components.webui_plugins']


def test_finalize_builds_manifest_only_for_plugins_declaring_a_ui_slot(tmp_path, webui_plugins):
    _register_fake_plugin(tmp_path, 'sleep_timer', slot='player', entry='ui.js')
    _register_fake_plugin(tmp_path, 'core_component')  # no PLUGIN_UI_SLOT/ENTRY -- must be ignored

    webui_plugins.finalize()

    manifest = webui_plugins.get_manifest()
    assert len(manifest) == 1
    assert manifest[0]['name'] == 'sleep_timer'
    assert manifest[0]['slot'] == 'player'
    assert manifest[0]['url'].endswith('/sleep_timer/ui.js')


def test_finalize_skips_plugin_with_missing_static_file(tmp_path, webui_plugins):
    _register_fake_plugin(tmp_path, 'broken', slot='player', entry='ui.js', create_static_file=False)

    webui_plugins.finalize()

    assert webui_plugins.get_manifest() == []


def test_finalize_does_not_start_server_when_nothing_to_serve(tmp_path, webui_plugins):
    _register_fake_plugin(tmp_path, 'core_component')

    webui_plugins.finalize()

    webui_plugins._UiExtensionServer.assert_not_called()


def test_finalize_starts_server_when_a_plugin_has_a_ui_extension(tmp_path, webui_plugins):
    _register_fake_plugin(tmp_path, 'sleep_timer', slot='player', entry='ui.js')

    webui_plugins.finalize()

    webui_plugins._UiExtensionServer.assert_called_once()


def test_get_manifest_is_empty_before_finalize_runs(webui_plugins):
    assert webui_plugins.get_manifest() == []
