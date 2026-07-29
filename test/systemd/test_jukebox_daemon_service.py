from configparser import ConfigParser
from pathlib import Path


def test_pipewire_pulse_is_required_and_ordered():
    service_path = (
        Path(__file__).parents[2]
        / 'resources'
        / 'default-services'
        / 'jukebox-daemon.service'
    )
    service = ConfigParser(interpolation=None)
    service.read(service_path)

    unit = service['Unit']
    assert 'pipewire-pulse.service' in unit['Requires'].split()
    assert 'pipewire-pulse.service' in unit['After'].split()
