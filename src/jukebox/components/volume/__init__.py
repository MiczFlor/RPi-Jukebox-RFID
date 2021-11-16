import collections
import logging
import threading
import time

import pulsectl
import jukebox.cfghandler
import jukebox.plugs as plugin
from components.volume.volumebase import VolumeBaseClass
from typing import (Dict)

logger = logging.getLogger('jb.pulse')
cfg = jukebox.cfghandler.get_handler('jukebox')


_lock_module = threading.RLock()

pulse_inst: pulsectl.Pulse


class PulseMonitor(threading.Thread):
    def __init__(self):
        super().__init__(name='PulseMon')
        self.daemon = True
        self._keep_running = True
        self.trigger = threading.Event()
        self.last_event = None
        # Access to self._in_wait is atomic!
        self._in_wait = False

    def stop(self):
        logger.debug('*' * 20 + 'STOP')
        self._keep_running = False
        self.trigger.set()
        # From the pulsectl doc: be sure to call it in a loop until event_listen returns or something
        while self._in_wait:
            pulse_inst.event_listen_stop()
            time.sleep(0.01)

    def pause(self):
        logger.debug('*' * 20 + 'PAUSE')
        # From the pulsectl doc: be sure to call it in a loop until event_listen returns or something
        while self._in_wait:
            pulse_inst.event_listen_stop()
            time.sleep(0.01)

    def resume(self):
        logger.debug('*' * 20 + 'RESUME')
        self.trigger.set()

    def __enter__(self):
        self.pause()
        _lock_module.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        _lock_module.release()
        self.resume()

    def get_event(self, event: pulsectl.PulseEventInfo):
        logger.debug(f'Pulse event: {event}')
        # This access is exclusive with handle_event access in the same thread: No need to lock
        self.last_event = event
        # This causes pulse_inst.event_listen to exit (w/o an exception!)
        raise pulsectl.PulseLoopStop

    def handle_event(self):
        # Event handling must happen outside Event Loop
        # logger.debug(f'----- Handle Event Start')
        # with _lock_module:
        logger.debug(f'----- Handle Event Locked')
        if self.last_event.facility == 'card' and self.last_event.t == 'new':
            logger.debug(f'New card detected')
            logger.info(f'Audio sink is now: {pulse_inst.server_info().default_sink_name}')
        elif self.last_event.facility == 'card' and self.last_event.t == 'remove':
            logger.debug(f'Disconnection detected')
            logger.info(f'Audio sink is now: {pulse_inst.server_info().default_sink_name}')
        if self.last_event.facility == 'sink' and self.last_event.t == 'change':
            logger.debug(f'Sink change detected (Volume: {pulse_control._get_volume()})')
            # logger.debug(f'Sink change detected (Volume: ...)')
        # This happens outside the active Event Loop: Strictly speaking no need to lock self.last_event
        self.last_event = None
        logger.debug('----- Handle Event Stop')

    def run(self) -> None:
        # <Enum event-mask [all autoload card client module null sample_cache server sink sink_input source source_output]>
        pulse_inst.event_mask_set('card', 'sink')
        pulse_inst.event_callback_set(self.get_event)
        while self._keep_running:
            logger.debug('*' * 20 + 'Start listening')
            self.trigger.clear()
            self._in_wait = True
            pulse_inst.event_listen(timeout=None)
            self._in_wait = False
            logger.debug('*' * 20 + 'Stop listening')
            if self.last_event is not None:
                with _lock_module:
                    try:
                        self.handle_event()
                    except Exception as e:
                        logger.error(f'Exception in handling event callback: {e.__class__.__name__}: {e}')
                    finally:
                        self.trigger.set()

            logger.debug('*' * 20 + 'Waiting for resume command')
            self.trigger.wait()
        logger.debug('*' * 20 + 'Exiting Monitor')


class PulseVolumeControl:
    def __init__(self):
        pass

    @plugin.tag
    def set_volume(self, volume):
        with pulse_monitor:
            name = pulse_inst.server_info().default_sink_name
            sink = pulse_inst.get_sink_by_name(name)
            logger.debug('*' * 20 + 'Set volume')
            pulse_inst.volume_set_all_chans(sink, volume / 100.0)

    def _get_volume(self):
        sink = pulse_inst.get_sink_by_name(pulse_inst.server_info().default_sink_name)
        logger.debug('*' * 20 + 'Get volume')
        volume = int(100 * pulse_inst.volume_get_all_chans(sink))
        return volume

    @plugin.tag
    def get_volume(self):
        with pulse_monitor:
            volume = self._get_volume()
        logger.debug('*' * 20 + f'Get volume return = {volume}')
        return volume


pulse_control: PulseVolumeControl
pulse_monitor: PulseMonitor


@plugin.initialize
def initialize():
    global pulse_inst
    global pulse_control
    global pulse_monitor
    pulse_inst = pulsectl.Pulse('jukebox-client')
    pulse_control = PulseVolumeControl()
    plugin.register(pulse_control, package="volume", name="ctrl", replace=True)
    pulse_monitor = PulseMonitor()
    pulse_monitor.start()


@plugin.finalize
def finalize():
    global pulse_control
    global pulse_monitor
    time.sleep(2)
    pulse_control.set_volume(30)
    # pulse_monitor.pause()
    # volume = 30
    # name = pulse_inst.server_info().default_sink_name
    # sink = pulse_inst.get_sink_by_name(name)
    # pulse_inst.volume_set_all_chans(sink, volume / 100.0)
    # pulse_monitor.resume()

    time.sleep(10)
    pulse_control.set_volume(40)
    # pulse_monitor.pause()
    # volume = 40
    # name = pulse_inst.server_info().default_sink_name
    # sink = pulse_inst.get_sink_by_name(name)
    # pulse_inst.volume_set_all_chans(sink, volume / 100.0)
    # pulse_monitor.resume()



@plugin.atexit
def atexit(**ignored_kwargs):
    global pulse_monitor
    pulse_monitor.stop()
