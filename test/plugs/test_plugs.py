import sys
import os
sys.path.append(os.path.abspath('../../src/jukebox'))

from importlib.metadata import EntryPoint  # noqa: E402
import pytest  # noqa: E402

import jukebox.plugs as plugs  # noqa: E402


@pytest.fixture(autouse=True)
def _reset_plugs_registry():
    """Every test starts and ends with a clean plugs registry -- these are module-level globals
    shared across the whole test session otherwise."""
    plugs._PLUGINS.clear()
    plugs._PACKAGE_MAP.clear()
    plugs._PLUGINS_FAILED.clear()
    yield
    plugs._PLUGINS.clear()
    plugs._PACKAGE_MAP.clear()
    plugs._PLUGINS_FAILED.clear()


@pytest.fixture
def fixture_package(tmp_path, monkeypatch):
    """A small importable python package with two loadable submodules, used as stand-ins for real
    plugin packages. Created fresh per test under tmp_path so tests can't interfere with each other."""
    pkg_name = 'plugs_fixture_pkg'
    pkg_dir = tmp_path / pkg_name
    pkg_dir.mkdir()
    (pkg_dir / '__init__.py').write_text('')
    (pkg_dir / 'plugin_a.py').write_text(
        "import jukebox.plugs as plugin\n"
        "@plugin.register\n"
        "def hello():\n"
        "    return 'hello from a'\n"
    )
    (pkg_dir / 'plugin_b.py').write_text(
        "import jukebox.plugs as plugin\n"
        "@plugin.register\n"
        "def hello():\n"
        "    return 'hello from b'\n"
    )

    monkeypatch.syspath_prepend(str(tmp_path))
    yield pkg_name

    for name in list(sys.modules):
        if name == pkg_name or name.startswith(f'{pkg_name}.'):
            del sys.modules[name]


class TestLoadAllNamed:
    def test_loads_all_given_packages_under_their_name(self, fixture_package):
        plugs.load_all_named({
            'a': f'{fixture_package}.plugin_a',
            'b': f'{fixture_package}.plugin_b',
        })

        assert set(plugs.get_all_loaded_packages().keys()) == {'a', 'b'}
        assert plugs.call('a', 'hello') == 'hello from a'
        assert plugs.call('b', 'hello') == 'hello from b'

    def test_preserves_mapping_order(self, fixture_package):
        # Order matters for core components (fixed dependency order) -- load_all_named must not
        # reorder what it's given.
        plugs.load_all_named({
            'second': f'{fixture_package}.plugin_b',
            'first': f'{fixture_package}.plugin_a',
        })

        assert list(plugs.get_all_loaded_packages().keys()) == ['second', 'first']

    def test_ignore_errors_skips_failed_package_but_loads_the_rest(self, fixture_package):
        plugs.load_all_named({
            'a': f'{fixture_package}.plugin_a',
            'missing': f'{fixture_package}.does_not_exist',
        }, ignore_errors=True)

        assert 'a' in plugs.get_all_loaded_packages()
        assert 'missing' not in plugs.get_all_loaded_packages()

    def test_without_ignore_errors_raises(self, fixture_package):
        with pytest.raises(Exception):
            plugs.load_all_named({'missing': f'{fixture_package}.does_not_exist'}, ignore_errors=False)


class TestGetModule:
    def test_returns_the_loaded_module(self, fixture_package):
        plugs.load(f'{fixture_package}.plugin_a', load_as='a')

        module = plugs.get_module('a')

        assert module.__name__ == f'{fixture_package}.plugin_a'
        assert module.hello() == 'hello from a'


class TestLoadAllEntryPoints:
    @staticmethod
    def _fake_entry_points(monkeypatch, entry_points, group='jukebox.plugins'):
        def fake_entry_points(*, group=None):
            return [ep for ep in entry_points if ep.group == group]
        monkeypatch.setattr(plugs.importlib.metadata, 'entry_points', fake_entry_points)

    def test_only_loads_explicitly_enabled_plugins(self, fixture_package, monkeypatch):
        self._fake_entry_points(monkeypatch, [
            EntryPoint(name='pkg_a', value=f'{fixture_package}.plugin_a', group='jukebox.plugins'),
            EntryPoint(name='pkg_b', value=f'{fixture_package}.plugin_b', group='jukebox.plugins'),
        ])

        plugs.load_all_entry_points(enabled=['pkg_a'])

        assert set(plugs.get_all_loaded_packages().keys()) == {'pkg_a'}

    def test_loads_enabled_plugins_in_the_given_order(self, fixture_package, monkeypatch):
        self._fake_entry_points(monkeypatch, [
            EntryPoint(name='pkg_a', value=f'{fixture_package}.plugin_a', group='jukebox.plugins'),
            EntryPoint(name='pkg_b', value=f'{fixture_package}.plugin_b', group='jukebox.plugins'),
        ])

        plugs.load_all_entry_points(enabled=['pkg_b', 'pkg_a'])

        assert list(plugs.get_all_loaded_packages().keys()) == ['pkg_b', 'pkg_a']

    def test_reports_installed_but_not_enabled_plugins_as_inactive(self, fixture_package, monkeypatch):
        self._fake_entry_points(monkeypatch, [
            EntryPoint(name='pkg_a', value=f'{fixture_package}.plugin_a', group='jukebox.plugins'),
            EntryPoint(name='pkg_b', value=f'{fixture_package}.plugin_b', group='jukebox.plugins'),
        ])

        inactive = plugs.load_all_entry_points(enabled=['pkg_a'])

        assert inactive == ['pkg_b']

    def test_enabled_name_not_installed_raises_by_default(self, monkeypatch):
        self._fake_entry_points(monkeypatch, [])

        with pytest.raises(NameError):
            plugs.load_all_entry_points(enabled=['does_not_exist'])

    def test_enabled_name_not_installed_ignored_when_requested(self, monkeypatch):
        self._fake_entry_points(monkeypatch, [])

        inactive = plugs.load_all_entry_points(enabled=['does_not_exist'], ignore_errors=True)

        assert inactive == []
        assert plugs.get_all_loaded_packages() == {}
