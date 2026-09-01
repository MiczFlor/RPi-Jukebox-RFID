import importlib
import sys
from unittest.mock import Mock, sentinel

import jukebox.plugs as plugs


def test_compatibility_player_entrypoint_configures_optional_backends(monkeypatch):
    monkeypatch.setattr(plugs, 'ALLOW_DIRECT_IMPORTS', True)
    sys.modules.pop('components.playermpd', None)
    module = importlib.import_module('components.playermpd')
    initialize_mpd = Mock(return_value=sentinel.coordinator)
    configure_spotify = Mock()
    monkeypatch.setattr(module, 'initialize_mpd_player', initialize_mpd)
    monkeypatch.setattr(module, 'configure_spotify', configure_spotify)

    module.initialize()

    initialize_mpd.assert_called_once_with('components.playermpd')
    configure_spotify.assert_called_once_with(sentinel.coordinator)
