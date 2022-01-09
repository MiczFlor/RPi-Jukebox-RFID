"""
Provide connector functions to hook up output devices with some kind of functionality
"""

import components.volume
import components.rfid.reader
import components.gpio.gpioz.plugin


def register_rfid_callback(device):

    def rfid_callback(card_id: str, state: int):
        if state == 0:
            device.blink(on_time=0.3, n=1)
        elif state == 1:
            device.blink(on_time=0.3, off_time=0.3, n=3)

    components.rfid.reader.add_rfid_card_detect_callback(
        func=rfid_callback)


def register_audio_sink_change_callback(device):

    def audio_sink_change_callback(alias, sink_name, sink_index, error_state):
        # logger.debug(f'Secondary audio sink LED status set callback: {sink_index} // {error_state}')
        if error_state:
            device.blink(on_time=0.4, off_time=0.4, n=3, background=True)
        elif sink_index == 1:
            device.on()
        else:
            device.off()

    components.volume.add_on_output_change_callbacks(
        func=audio_sink_change_callback)


def register_volume_led_callback(device):

    def audio_volume_change_callback(volume):
        # We need a non-linear scaling, to give a visually
        # constant brightness change across the volume range
        device.value = float(volume * volume) / 10000.0

    components.volume.add_on_volume_change_callback(
        func=audio_volume_change_callback)


def register_status_led_callback(device):

    def set_status_led(state):
        if state > 1:
            device.blink(on_time=0.1, off_time=0.1, n=None, background=True)
        elif state == 1:
            device.on()
        else:
            device.off()

    components.gpio.gpioz.plugin.add_status_callback(set_status_led)


def register_status_buzzer_callback(device):

    def set_status_buzzer(state):
        if state == 1:
            device.beep(on_time=1.0, n=1)
        else:
            device.beep(on_time=0.5, off_time=0.2, n=2)

    components.gpio.gpioz.plugin.add_status_callback(set_status_buzzer)
