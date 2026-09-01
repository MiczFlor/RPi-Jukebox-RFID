import importlib.util
from pathlib import Path

from ruamel.yaml import YAML


SCRIPT = (
    Path(__file__).parents[2]
    / 'installation'
    / 'components'
    / 'configure_spotify.py'
)
SPEC = importlib.util.spec_from_file_location('configure_spotify', SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_configure_spotify_preserves_yaml_and_sets_player_values(tmp_path):
    config_path = tmp_path / 'jukebox.yaml'
    config_path.write_text(
        'system:\n'
        '  box_name: Test box\n'
        'players:\n'
        '  spotify:\n'
        '    enabled: false\n'
        '    token_file: tokens.json\n',
    )

    MODULE.configure(
        config_path,
        'client-id',
        'https://box.example/api/v1/spotify/oauth/callback',
        'Kitchen Phoniebox',
    )

    with config_path.open() as stream:
        config = YAML(typ='safe').load(stream)
    assert config['system']['box_name'] == 'Test box'
    assert config['players']['spotify'] == {
        'enabled': True,
        'client_id': 'client-id',
        'redirect_uri': 'https://box.example/api/v1/spotify/oauth/callback',
        'device_name': 'Kitchen Phoniebox',
        'token_file': 'tokens.json',
    }
