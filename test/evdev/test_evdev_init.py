""" Tests for the evdev __init__ module
"""
import sys
import unittest
from unittest.mock import patch
from unittest.mock import MagicMock

# Before importing the module, the jukebox.plugs decorators need to be patched
# to not try to register the plugins
import jukebox.plugs as plugin


def dummy_decorator(fkt):
    return fkt


plugin.register = dummy_decorator
plugin.initialize = dummy_decorator
plugin.atexit = dummy_decorator

# Mock the jukebox.publishing module to prevent issues with zmq
# which is currently hard to install(see issue #2050)
# and not installed properly for CI
sys.modules['jukebox.publishing'] = MagicMock()

# Import uses the patched decorators
from components.controls.event_devices import _input_devices_to_key_mapping  # noqa: E402
from components.controls.event_devices import parse_device_config  # noqa: E402


class TestInputDevicesToKeyMapping(unittest.TestCase):
    def test_mapping_with_supported_input_type_and_key_code(self):
        input_devices = {
            'device1': {
                'type': 'Button',
                'kwargs': {
                    'key_code': 123
                },
                'actions': {
                    'on_press': 'action1'
                }
            },
            'device2': {
                'type': 'Button',
                'kwargs': {
                    'key_code': 456
                },
                'actions': {
                    'on_press': 'action2'
                }
            }
        }

        expected_mapping = {
            123: 'action1',
            456: 'action2'
        }

        mapping = _input_devices_to_key_mapping(input_devices)

        self.assertEqual(mapping, expected_mapping)

    def test_mapping_with_missing_type(self):
        input_devices = {
            'device1': {
                'kwargs': {
                    'key_code': 123
                },
                'actions': {
                    'on_press': 'action1'
                }
            }
        }

        expected_mapping = {}

        mapping = _input_devices_to_key_mapping(input_devices)

        self.assertEqual(mapping, expected_mapping)

    def test_mapping_with_unsupported_input_type(self):
        input_devices = {
            'device1': {
                'type': 'unknown',
                'kwargs': {
                    'key_code': 'A'
                },
                'actions': {
                    'on_press': 'action1'
                }
            }
        }

        mapping = _input_devices_to_key_mapping(input_devices)

        self.assertEqual(mapping, {})

    def test_mapping_with_missing_key_code(self):
        input_devices = {
            'device1': {
                'type': 'button',
                'kwargs': {},
                'actions': {
                    'on_press': 'action1'
                }
            }
        }

        mapping = _input_devices_to_key_mapping(input_devices)

        self.assertEqual(mapping, {})

    def test_mapping_with_unsupported_action(self):
        input_devices = {
            'device1': {
                'type': 'button',
                'kwargs': {
                    'key_code': 'A'
                },
                'actions': {
                    'unknown_action': 'action1'
                }
            }
        }

        mapping = _input_devices_to_key_mapping(input_devices)

        self.assertEqual(mapping, {})


class TestParseDeviceConfig(unittest.TestCase):
    @patch('components.controls.event_devices.jukebox.utils.bind_rpc_command')
    def test_parse_device_config(self, bind_rpc_command_mock):
        config = {
            "device_name": "Test Device",
            "exact": True,
            "input_devices": {
                'device1': {
                    'type': 'Button',
                    'kwargs': {'key_code': 123},
                    'actions': {
                        'on_press': 'action1'
                    }
                }
            }
        }

        device_name, exact, button_callbacks = parse_device_config(config)
        self.assertEqual(device_name, "Test Device")
        self.assertEqual(exact, True)
        self.assertEqual(button_callbacks, {
            123: bind_rpc_command_mock.return_value,
        })

    def test_parse_device_config_missing_input_devices(self):
        config = {
            "device_name": "Test Device",
            "exact": True
        }
        device_name, exact, button_callbacks = parse_device_config(config)
        self.assertEqual(device_name, "Test Device")
        self.assertEqual(exact, True)
        self.assertEqual(button_callbacks, {})

    def test_parse_device_config_missing_device_name(self):
        config = {
            "exact": True,
            "input_devices": {}
        }
        self.assertRaises(ValueError, parse_device_config, config)

    def test_parse_device_config_missing_exact(self):
        """Test that the default value for exact is False"""
        config = {
            "device_name": "Test Device",
            "input_devices": {}
        }
        device_name, exact, button_callbacks = parse_device_config(config)
        self.assertEqual(device_name, "Test Device")
        self.assertEqual(exact, False)
        self.assertEqual(button_callbacks, {})


if __name__ == '__main__':
    unittest.main()
