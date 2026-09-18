import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).parents[2]
DEFAULTS = ROOT / 'installation' / 'includes' / '01_default_config.sh'
OPTIONS = ROOT / 'installation' / 'routines' / 'customize_options.sh'
SETUP = ROOT / 'installation' / 'routines' / 'setup_spotify.sh'
DEFAULT_REDIRECT_URI = (
    'http://127.0.0.1:3000/api/v1/spotify/oauth/callback'
)


def _run_spotify_options(user_input, redirect_uri=None):
    harness = r'''
DEFAULTS_PATH="$1"
OPTIONS_PATH="$2"

clear_c() {
    :
}

print_c() {
    printf '%s\n' "$1"
}

log() {
    :
}

source "${DEFAULTS_PATH}"
source "${OPTIONS_PATH}"
_option_spotify
printf '%s\n' "${SPOTIFY_REDIRECT_URI}"
'''
    env = os.environ.copy()
    if redirect_uri is not None:
        env['SPOTIFY_REDIRECT_URI'] = redirect_uri
    else:
        env.pop('SPOTIFY_REDIRECT_URI', None)

    return subprocess.run(
        [
            'bash',
            '-c',
            harness,
            'test-spotify-options',
            str(DEFAULTS),
            str(OPTIONS),
        ],
        input=user_input,
        check=False,
        capture_output=True,
        env=env,
        text=True,
    )


def test_spotify_options_use_standard_redirect_uri_by_default():
    result = _run_spotify_options('y\n\nclient-id\n\n')

    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines()[-1] == DEFAULT_REDIRECT_URI
    assert 'https://developer.spotify.com/dashboard' in result.stdout
    assert f'   {DEFAULT_REDIRECT_URI}' in result.stdout
    assert 'ssh -L 3000:127.0.0.1:80 ' in result.stdout
    assert 'browse to http://127.0.0.1:3000' in result.stdout
    assert 'Settings > Spotify > Connect' in result.stdout


def test_spotify_options_accept_custom_redirect_uri():
    redirect_uri = 'https://phoniebox.example/api/v1/spotify/oauth/callback'
    result = _run_spotify_options(f'y\n{redirect_uri}\nclient-id\n\n')

    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines()[-1] == redirect_uri
    assert f'   {redirect_uri}' in result.stdout
    assert 'ssh -L' not in result.stdout


def test_spotify_options_preserve_preconfigured_redirect_uri():
    redirect_uri = 'https://configured.example/api/v1/spotify/oauth/callback'
    result = _run_spotify_options(
        'y\nclient-id\n\n',
        redirect_uri=redirect_uri,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines()[-1] == redirect_uri
    assert f'   {redirect_uri}' in result.stdout


def _spotify_finish_message(redirect_uri):
    harness = r'''
DEFAULTS_PATH="$1"
SETUP_PATH="$2"

source "${DEFAULTS_PATH}"
source "${SETUP_PATH}"

CURRENT_USER=pi
SPOTIFY_DEVICE_NAME="Test Phoniebox"
SPOTIFY_REDIRECT_URI="$3"
FIN_MESSAGE=""
hostname() {
    printf '%s\n' test-phoniebox
}

_spotify_append_finish_message
printf '%b\n' "${FIN_MESSAGE}"
'''
    return subprocess.run(
        [
            'bash',
            '-c',
            harness,
            'test-spotify-finish-message',
            str(DEFAULTS),
            str(SETUP),
            redirect_uri,
        ],
        check=False,
        capture_output=True,
        text=True,
    )


def test_spotify_finish_message_explains_default_redirect_tunnel():
    result = _spotify_finish_message(DEFAULT_REDIRECT_URI)

    assert result.returncode == 0, result.stderr
    assert (
        'ssh -L 3000:127.0.0.1:80 pi@test-phoniebox.local'
        in result.stdout
    )
    assert 'browse to http://127.0.0.1:3000' in result.stdout
    assert 'Settings > Spotify > Connect' in result.stdout


def test_spotify_finish_message_uses_custom_redirect_without_tunnel():
    redirect_uri = 'https://phoniebox.example/api/v1/spotify/oauth/callback'
    result = _spotify_finish_message(redirect_uri)

    assert result.returncode == 0, result.stderr
    assert redirect_uri in result.stdout
    assert 'ssh -L' not in result.stdout
