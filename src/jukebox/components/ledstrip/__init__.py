"""
LED strip plugin for Phoniebox.

Controls an LED strip connected to a Raspberry Pi Pico over USB-Serial.
Reacts to RPC commands (e.g. from GPIO buttons) and to player status changes.
"""

import zmq
import threading
import json
import logging

import jukebox.plugs as plugin
import jukebox.cfghandler

from .pico_controller import PicoLedController

logger = logging.getLogger('jb.LedStrip')
cfg_main = jukebox.cfghandler.get_handler('jukebox')

DEFAULT_EFFECTS = {
    'play': 'fill 0 255 0',
    'pause': 'fill 255 165 0',
    'stop': 'off',
    'toggle': 'fill 0 255 0',
    'volume_up': 'chase 0 255 0 20',
    'volume_down': 'chase 255 0 0 20',
    'next_song': 'chase 255 255 255 30',
    'prev_song': 'chase 0 0 255 30',
    'next_folder': 'rainbow 10',
    'prev_folder': 'rainbow 50',
    'repeat': 'chase 0 0 255 20',
}


class PlayerStatusSubscriber:
    """
    Listen to playerstatus events and trigger LED effects for play/pause/stop.
    """

    def __init__(self, controller: PicoLedController, effects: dict):
        self.controller = controller
        self.effects = effects
        self.ctx = zmq.Context.instance()
        self.sub = self.ctx.socket(zmq.SUB)
        self.sub.connect('inproc://PublisherToProxy')
        self.sub.setsockopt(zmq.SUBSCRIBE, b'playerstatus')
        self.running = True
        self.thread = threading.Thread(target=self._event_loop, daemon=True, name='LedStripSubscriber')
        self._last_state = None

    def start(self):
        self.thread.start()
        logger.info('LED strip subscriber started')

    def stop(self):
        self.running = False
        self.sub.close()
        self.thread.join(timeout=2.0)
        self._run_effect('stop')
        logger.info('LED strip subscriber stopped')

    def _event_loop(self):
        while self.running:
            try:
                topic, message = self.sub.recv_multipart()
            except zmq.ZMQError:
                break

            if not self.running:
                break

            try:
                status = json.loads(message)
            except json.JSONDecodeError as e:
                logger.error(f'Error decoding playerstatus JSON: {e}')
                continue

            state = status.get('state', 'stop')
            if state == self._last_state:
                continue
            self._last_state = state

            if state == 'play':
                self._run_effect('play')
            elif state == 'pause':
                self._run_effect('pause')
            elif state == 'stop':
                self._run_effect('stop')

    def _run_effect(self, name: str):
        command = self.effects.get(name)
        if command:
            self.controller.send(command)


_controller = None
_subscriber = None


def _run_effect(name: str):
    global _controller
    if _controller is None:
        return
    command = _controller['effects'].get(name)
    if command:
        _controller['instance'].send(command)


@plugin.register
def play():
    _run_effect('play')


@plugin.register
def toggle():
    _run_effect('toggle')


@plugin.register
def volume_up():
    _run_effect('volume_up')


@plugin.register
def volume_down():
    _run_effect('volume_down')


@plugin.register
def next_song():
    _run_effect('next_song')


@plugin.register
def prev_song():
    _run_effect('prev_song')


@plugin.register
def next_folder():
    _run_effect('next_folder')


@plugin.register
def prev_folder():
    _run_effect('prev_folder')


@plugin.register
def repeat():
    _run_effect('repeat')


@plugin.initialize
def initialize():
    global _controller, _subscriber

    enable = cfg_main.setndefault('ledstrip', 'enable', value=False)
    if not enable:
        return

    port = cfg_main.setndefault('ledstrip', 'port', value='/dev/ttyACM0')
    effects_cfg = cfg_main.getn('ledstrip', 'effects') or {}
    effects = {**DEFAULT_EFFECTS, **effects_cfg}

    controller = PicoLedController(port=port)
    _controller = {
        'instance': controller,
        'effects': effects,
    }

    _subscriber = PlayerStatusSubscriber(controller, effects)
    _subscriber.start()


@plugin.atexit
def atexit(**ignored_kwargs):
    global _subscriber
    if _subscriber is not None:
        _subscriber.stop()
