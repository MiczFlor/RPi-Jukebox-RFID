from configparser import ConfigParser
from pathlib import Path


SERVICES = Path(__file__).parents[2] / 'resources' / 'default-services'


def test_librespot_uses_pipewire_pulse_and_fixed_volume():
    service = ConfigParser(interpolation=None)
    service.read(SERVICES / 'librespot.service')

    unit = service['Unit']
    assert 'pipewire-pulse.service' in unit['Requires'].split()
    assert 'pipewire-pulse.service' in unit['After'].split()

    command = service['Service']['ExecStart']
    assert '--backend pulseaudio' in command
    assert '--volume-ctrl fixed' in command
    assert '--system-cache %h/.cache/librespot' in command


def test_spotify_dropin_only_adds_optional_jukebox_dependency():
    dropin = ConfigParser(interpolation=None)
    dropin.read(SERVICES / 'jukebox-spotify.conf')

    unit = dropin['Unit']
    assert unit['Wants'] == 'librespot.service'
    assert unit['After'] == 'librespot.service'
