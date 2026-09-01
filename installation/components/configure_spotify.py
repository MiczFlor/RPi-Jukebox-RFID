#!/usr/bin/env python3
"""Enable the Spotify player in an installed Jukebox YAML file."""

import argparse
from pathlib import Path

from ruamel.yaml import YAML


def configure(config_path, client_id, redirect_uri, device_name):
    yaml = YAML(typ='rt')
    with config_path.open(encoding='utf-8') as stream:
        config = yaml.load(stream)

    spotify = config.setdefault('players', {}).setdefault('spotify', {})
    spotify['enabled'] = True
    spotify['client_id'] = client_id
    spotify['redirect_uri'] = redirect_uri
    spotify['device_name'] = device_name

    with config_path.open('w', encoding='utf-8') as stream:
        yaml.dump(config, stream)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('config', type=Path)
    parser.add_argument('--client-id', required=True)
    parser.add_argument('--redirect-uri', required=True)
    parser.add_argument('--device-name', default='Phoniebox')
    args = parser.parse_args()

    configure(
        args.config,
        args.client_id,
        args.redirect_uri,
        args.device_name,
    )


if __name__ == '__main__':
    main()
