import unittest
from unittest.mock import MagicMock

# Patching the plugin decorators
import jukebox.plugs as plugin

def dummy_decorator(fkt):
    return fkt

plugin.register = dummy_decorator
plugin.initialize = dummy_decorator
plugin.atexit = dummy_decorator

from components.controls.event_devices import _input_devices_to_key_mapping

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

if __name__ == '__main__':
    unittest.main()