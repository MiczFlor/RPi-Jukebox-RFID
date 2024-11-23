# RPi-Jukebox-RFID Version 3
# Copyright (c) See file LICENSE in project root folder
"""PulseAudio Volume Control Plugin Package

## Features

* Volume Control
* Two outputs
* Watcher thread on volume / output change

## Publishes

* volume.level
* volume.sink

## PulseAudio References

<https://brokkr.net/2018/05/24/down-the-drain-the-elusive-default-pulseaudio-sink/>

Check fallback device (on device de-connect):

    $ pacmd list-sinks | grep -e 'name:' -e 'index'


## Integration

Pulse Audio runs as a user process. Processes who want to communicate / stream to it
must also run as a user process.

This means must also run as user process, as described in
[Music Player Daemon](../../builders/system.md#music-player-daemon-mpd).

## Misc

PulseAudio may switch the sink automatically to a connecting bluetooth device depending on the loaded module
with name module-switch-on-connect. On Raspberry Pi OS Bullseye, this module is not part of the default configuration
in ``/usr/pulse/default.pa``. So, we don't need to worry about it.
If the module gets loaded it conflicts with the toggle on connect and the selected primary / secondary outputs
from the Jukebox. Remove it from the configuration!

    ### Use hot-plugged devices like Bluetooth or USB automatically (LP: #1702794)
    ### not available on PI?
    .ifexists module-switch-on-connect.so
    load-module module-switch-on-connect
    .endif

## Why PulseAudio?

The audio configuration of the system is one of those topics,
which has a myriad of options and possibilities. Every system is different and PulseAudio unifies these and
makes our life easier. Besides, it is only option to support Bluetooth at the moment.

## Callbacks:

The following callbacks are provided. Register callbacks with these adder functions (see their documentation for details):

1. :func:`add_on_connect_callback`
2. :func:`add_on_output_change_callbacks`
3. :func:`add_on_volume_change_callback`
"""
import collections
import logging
import threading
import time
import traceback

import pulsectl
import jukebox.cfghandler
import jukebox.plugs as plugin
import jukebox.publishing as publishing
from typing import (List, Optional, Callable)
from jukebox.callingback import CallbackHandler

logger = logging.getLogger('jb.pulse')
logger_event = logging.getLogger('jb.pulse.event')
cfg = jukebox.cfghandler.get_handler('jukebox')


_lock_module = threading.RLock()


def clamp(n, minn, maxn):
    return min(max(n, minn), maxn)


PulseAudioSinkClass = collections.namedtuple('PaSink', ['alias',
                                                        'pulse_sink_name',
                                                        'volume_limit'])


class PulseMonitor(threading.Thread):
    """A thread for monitoring and interacting with the Pulse Lib via pulsectrl

    Whenever we want to access pulsectl, we need to exit the event listen loop.
    This is handled by the context manager. It stops the event loop and returns
    the pulsectl instance to be used (it does no return the monitor thread itself!)

    The context manager also locks the module to ensure proper thread sequencing,
    as only a single thread may work with pulsectl at any time. Currently, an RLock is
    used, even if it may not be necessary
    """

    class SoundCardConnectCallbacks(CallbackHandler):
        """
        Callbacks are executed when

            * new sound card gets connected

        """
        def register(self, func: Callable[[str, str], None]):
            """
            Add a new callback function :attr:`func`.

            Callback signature is

            .. py:function:: func(card_driver: str, device_name: str)
                :noindex:

            :param card_driver: The PulseAudio card driver module,
                e.g. :data:`module-bluez5-device.c` or :data:`module-alsa-card.c`
            :param device_name: The sound card device name as reported
                in device properties
            """
            super().register(func)

        def run_callbacks(self, sink_name, alias, sink_index, error_state):
            """:meta private:"""
            super().run_callbacks(sink_name, alias, sink_index, error_state)

    def __init__(self):
        super().__init__(name='PulseMon')
        self.daemon = True
        self._keep_running = True
        self.listen_done = threading.Event()
        self.action_done = threading.Event()
        self.last_event: List[pulsectl.PulseEventInfo] = []
        self._pulse_inst = pulsectl.Pulse('jukebox-client')
        self._toggle_on_connect = True

        # For the callback handler: We use the context lock only explicitly for registering new functions
        # When the callbacks are run, it happens from inside the pulse_monitor which an already acquired lock
        #: Callback handler instance for on_connect_callbacks events.
        #: See #PulseMonitor.SoundCardConnectCallbacks
        self.on_connect_callbacks: PulseMonitor.SoundCardConnectCallbacks = PulseMonitor.SoundCardConnectCallbacks(
            'on_connect_callback', logger, context=self)

    @property
    def toggle_on_connect(self):
        """Returns :data:`True` if the sound card shall be changed when a new card connects/disconnects. Setting this
        property changes the behavior.

        > [!NOTE]
        > A new card is always assumed to be the secondary device from the audio configuration.
        > At the moment there is no check it actually is the configured device. This means any new
        > device connection will initiate the toggle. This, however, is no real issue as the RPi's audio
        > system will be relatively stable once setup
        """
        return self._toggle_on_connect

    @toggle_on_connect.setter
    def toggle_on_connect(self, state=True):
        """Toggle Doc 2"""
        self._toggle_on_connect = state

    def __enter__(self):
        _lock_module.acquire()
        while not self.listen_done.is_set():
            self._pulse_inst.event_listen_stop()
            time.sleep(0.01)
        self.listen_done.clear()
        return self._pulse_inst

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.action_done.set()
        _lock_module.release()

    def stop(self):
        """Stop the pulse monitor thread"""
        logger.debug('Stop request received')
        _lock_module.acquire()
        try:
            self._keep_running = False
            while not self.listen_done.is_set():
                self._pulse_inst.event_listen_stop()
                time.sleep(0.01)
            self.listen_done.clear()
            self.action_done.set()
        finally:
            _lock_module.release()

    def _get_event(self, event: pulsectl.PulseEventInfo):
        if logger_event.isEnabledFor(logging.DEBUG):
            logger_event.debug(f'Received PulseAudio event: {event}')
        # This access is exclusive with handle_event access in the same thread: No need to lock
        # We can receive multiple events w/o them being handled in between
        self.last_event.append(event)
        # This causes self.pulse_inst.event_listen to exit (w/o an exception!)
        raise pulsectl.PulseLoopStop

    def _handle_event(self):
        # Event handling must happen outside PA Event Loop
        # Everything in here is within context already, meaning we MUST use the
        # pulse_control._* functions!
        current_event = self.last_event[0]
        if logger_event.isEnabledFor(logging.DEBUG):
            logger_event.debug(f'Handling PulseAudio event: {current_event}')
        if current_event.facility == 'card' and current_event.t == 'new':
            # Find the newly connected card
            for card_info in self._pulse_inst.card_list():
                if card_info.index == current_event.index:
                    # Alsa device drivers (HifiBerry, USB, etc...) have field 'alsa.card_name',
                    # bluetooth drivers have field 'device.description'. Any others? Don't know about other drivers -> Unknown
                    device_name = card_info.proplist.get('device.description',
                                                         card_info.proplist.get('alsa.card_name', 'Unknown'))
                    break
            else:
                # This should never happen!
                logger.error(f"Got new card event with index {current_event.index} but could not "
                             f"find card in {self._pulse_inst.card_list()}")
                return

            logger.info(f"New audio output detected: '{device_name}' "
                        f"(driver = {card_info.driver}, index {current_event.index})")

            # A new card is always assumed to be the Bluetooth device, as this is the only removable device
            if self._toggle_on_connect:
                pulse_control._set_output(self._pulse_inst, 1)
            # Context for running callbacks is already acquired
            self.on_connect_callbacks._run_callbacks(card_info.driver, device_name)
        elif current_event.facility == 'card' and current_event.t == 'remove':
            # An card has been removed. This could be any card, but for now we assume that it always is
            # the bluetooth device that has been removed, as we only have that one removable device
            # Minimum check: is it still in the sink list?
            # On disconnect PulseAudio, goes to fallback device
            # This can be checked with
            # pacmd list-sinks | grep -e 'name:' -e 'index'
            logger.info('Audio output disconnection detected')
            # For now we always go back to user defined primary device as
            # it could be different from what PulseAudio makes as the fallback device
            # (On Pis with a single sound card and a single bluetooth it makes  no difference, but also does not hurt)
            pulse_control._set_output(self._pulse_inst, 0)
            # When relying on PA default fallback situation, remember to publish the new output
            # alias, name = pulse_control._publish_outputs(self._pulse_inst)
            pulse_control._publish_volume(self._pulse_inst)
        if current_event.facility == 'sink' and current_event.t == 'change':
            pulse_control._publish_volume(self._pulse_inst)

    def run(self) -> None:
        """Starts the pulse monitor thread"""
        logger.info('Start Pulse Monitor Thread')
        # <Enum event-mask [all autoload card client module null sample_cache server sink sink_input source source_output]>
        self._pulse_inst.event_mask_set('card', 'sink')
        self._pulse_inst.event_callback_set(self._get_event)

        while self._keep_running:
            self._pulse_inst.event_listen(timeout=None)
            if not self.last_event:
                # Event loop has been stopped with event_loop_stop
                # Need to temporarily disable callbacks: otherwise we sporadically get events in the
                # MainThread even though event_listening is stopped. Why?
                self._pulse_inst.event_callback_set(None)
                self.listen_done.set()
                if logger_event.isEnabledFor(logging.DEBUG):
                    logger_event.debug('Waiting for action done command')
                # Gives control to action execution request
                self.action_done.wait()
                self.action_done.clear()
                self._pulse_inst.event_callback_set(self._get_event)
            else:
                while self.last_event:
                    try:
                        self._handle_event()
                    except Exception as e:
                        logger.error(f'Exception in handling event callback: {e.__class__.__name__}: {e}')
                    finally:
                        self.last_event.__delitem__(0)
        logger.info('Exit Pulse Monitor Thread')


class PulseVolumeControl:
    """Volume control manager for PulseAudio

    When accessing the pulse library, it needs to be put into a special
    state. Which is ensured by the context manager

        with pulse_monitor as pulse ...


    All private functions starting with `_function_name` assume that this is ensured by
    the calling function. All user functions acquire proper context!
    """

    class OutputChangeCallbackHandler(CallbackHandler):
        """
        Callbacks are executed when

            * audio sink is changed

        """
        def register(self, func: Callable[[str, str, int, int], None]):
            """
            Add a new callback function :attr:`func`.
            Parameters always give the valid audio sink. That means, if an error
            occurred, all parameters are valid.

            Callback signature is

            .. py:function:: func(sink_name: str, alias: str, sink_index: int, error_state: int)
                :noindex:

            :param sink_name: PulseAudio's sink name
            :param alias: The alias for :attr:`sink_name`
            :param sink_index: The index of the sink in the configuration list
            :param error_state: 1 if there was an attempt to change the output
               but an error occurred. Above parameters always give the now valid sink!
               If a sink change is successful, it is 0.
            """
            super().register(func)

        def run_callbacks(self, sink_name, alias, sink_index, error_state):
            """:meta private:"""
            super().run_callbacks(sink_name, alias, sink_index, error_state)

    class OutputVolumeCallbackHandler(CallbackHandler):
        """
        Callbacks are executed when

            * audio volume level is changed

        """
        def register(self, func: Callable[[int, bool, bool], None]):
            """
            Add a new callback function :attr:`func`.

            Callback signature is

            .. py:function:: func(volume: int, is_min: bool, is_max: bool)
                :noindex:

            :param volume: Volume level
            :param is_min: 1, if volume level is minimum, else 0
            :param is_max: 1, if volume level is maximum, else 0
            """
            super().register(func)

        def run_callbacks(self, sink_name, alias, sink_index, error_state):
            """:meta private:"""
            super().run_callbacks(sink_name, alias, sink_index, error_state)

    def __init__(self, sink_list: List[PulseAudioSinkClass]):
        self._sink_list: List[PulseAudioSinkClass] = sink_list
        logger.debug(f'Configured audio sinks: {self._sink_list}')
        # Prepare quick look-ups for volume_limit
        self._volume_limit = {x.pulse_sink_name: x.volume_limit / 100.0 for x in self._sink_list}
        self._soft_max_volume = cfg.setndefault('pulse', 'soft_max_volume', value=100)

        # For both callback handler: We use the context lock only explicitly for registering new functions
        # When the callbacks are run, it happens from inside the pulse_control which an already acquired lock

        #: Callback handler instance for on_output_change_callbacks events.
        #: See #PulseVolumeControl.OutputChangeCallbackHandler
        self.on_output_change_callbacks = PulseVolumeControl.OutputChangeCallbackHandler(
            'on_output_change_callbacks', logger, context=pulse_monitor)

        #: Callback handler instance for on_output_change_callbacks events.
        #: See #PulseVolumeControl.OutputVolumeCallbackHandler
        self.on_volume_change_callbacks = PulseVolumeControl.OutputVolumeCallbackHandler(
            'on_volume_change_callbacks', logger, context=pulse_monitor)

    def _set_volume(self, pulse_inst: pulsectl.Pulse, volume: int, sink_name: Optional[str] = None):
        # Set volume triggers should not trigger a volume change event,
        # as event listen is stopped. Need to manually publish volume
        # In some cases it still get registered as event, in which case volume is published twice
        if sink_name is None:
            sink_name = pulse_inst.server_info().default_sink_name
        sink = pulse_inst.get_sink_by_name(sink_name)
        # logger.debug('*' * 20 + 'Set volume')
        volume = min(volume, self._soft_max_volume)
        if volume == 0:
            pulse_inst.mute(sink, mute=True)
            pulse_inst.volume_set_all_chans(sink, 0)
        else:
            # Always make sure, we are not muted!
            pulse_inst.mute(sink, mute=False)
            volume = volume * self._volume_limit.get(sink_name, 1)
            pulse_inst.volume_set_all_chans(sink, volume / 100.0)
        self._publish_volume(pulse_inst)

    def _get_volume_and_mute(self, pulse_inst: pulsectl.Pulse, sink_name: Optional[str] = None):
        if sink_name is None:
            sink_name = pulse_inst.server_info().default_sink_name
        sink = pulse_inst.get_sink_by_name(sink_name)
        mute = sink.mute
        volume = int(round(100 * pulse_inst.volume_get_all_chans(sink) / self._volume_limit.get(sink_name, 1)))
        if mute == 1:
            volume = 0
        return volume, mute

    def _publish_volume(self, pulse_inst: pulsectl.Pulse):
        volume, mute = self._get_volume_and_mute(pulse_inst)
        publishing.get_publisher().send('volume.level', {'volume': volume, 'mute': mute})
        # Context for running callbacks is already acquired
        self.on_volume_change_callbacks._run_callbacks(volume, volume <= 0, volume >= self._soft_max_volume)
        return volume, mute

    def _get_outputs(self, pulse_inst: pulsectl.Pulse):
        sink_name = pulse_inst.server_info().default_sink_name
        sink_alias = 'Unset alias'
        for e in self._sink_list:
            if e.pulse_sink_name == sink_name:
                sink_alias = e.alias
                break
        return sink_alias, sink_name

    def _publish_outputs(self, pulse_inst: pulsectl.Pulse):
        sink_alias, sink_name = self._get_outputs(pulse_inst)

        publishing.get_publisher().send('volume.sink',
                                        {'active_alias': sink_alias,
                                         'active_sink': sink_name,
                                         'sink_list': [s._asdict() for s in self._sink_list]})
        return sink_alias, sink_name

    def _set_output(self, pulse_inst: pulsectl.Pulse, sink_index: int):
        error_state = 1
        if not 0 <= sink_index < len(self._sink_list):
            logger.error(f"Sink index '{sink_index}' out of range (0..{len(self._sink_list) - 1}). "
                         f"Did you configure your secondary output device?")
        else:
            # Before we switch the sink, check the new sinks volume levels...
            sink_name = self._sink_list[sink_index].pulse_sink_name
            try:
                sink = pulse_inst.get_sink_by_name(sink_name)
            except Exception as e:
                logger.error(f"Could not set output! Selected sink '{sink_name}' not in available "
                             f"sinks {[x.name for x in pulse_inst.sink_list()]} "
                             f"// {e.__class__.__name__}: {e}")
            else:
                volume, mute = self._get_volume_and_mute(pulse_inst, sink_name)
                if volume > self._soft_max_volume or volume > 100:
                    self._set_volume(pulse_inst, self._soft_max_volume, sink_name)
                # The existence of sink has already been checked above, but a disconnect in between
                # could (theoretically cause) a missing sink (todo)
                pulse_inst.default_set(sink)
                error_state = 0
        alias, sink_name = self._publish_outputs(pulse_inst)
        if self.on_output_change_callbacks.has_callbacks:
            sink_index = -1
            if sink_name == self._sink_list[0].pulse_sink_name:
                sink_index = 0
            elif len(self._sink_list) > 1 and sink_name == self._sink_list[1].pulse_sink_name:
                sink_index = 1
            # Context for running callbacks is already acquired
            self.on_output_change_callbacks._run_callbacks(sink_name, alias, sink_index, error_state)
        logger.info(f"Audio sink is now '{alias}' :: '{sink_name}'")
        self._publish_volume(pulse_inst)
        return alias, sink_name

    def _toggle_output(self, pulse_inst: pulsectl.Pulse):
        sink_name = pulse_inst.server_info().default_sink_name
        # Always default to index 0, unless we a in index 0; then switch to index 1
        sink_index = 0
        if sink_name == self._sink_list[0].pulse_sink_name:
            sink_index = 1
        return self._set_output(pulse_inst, sink_index)

    @plugin.tag
    def toggle_output(self):
        """Toggle the audio output sink"""
        with pulse_monitor as pulse:
            self._toggle_output(pulse)

    @plugin.tag
    def get_outputs(self):
        """Get current output and list of outputs"""
        with pulse_monitor as pulse:
            sink_alias, sink_name = self._get_outputs(pulse)
        return {'active_alias': sink_alias,
                'active_sink': sink_name,
                'sink_list': [s._asdict() for s in self._sink_list]}

    @plugin.tag
    def publish_volume(self):
        """Publish (volume, mute)"""
        with pulse_monitor as pulse:
            volume, mute = self._publish_volume(pulse)
        return volume, mute

    @plugin.tag
    def publish_outputs(self):
        """Publish current output and list of outputs"""
        with pulse_monitor as pulse:
            sink_alias, sink_name = self._publish_outputs(pulse)
        return sink_alias, sink_name

    @plugin.tag
    def set_volume(self, volume: int):
        """Set the volume (0-100) for the currently active output"""
        if not 0 <= volume <= 100:
            logger.warning(f"set_volume: volume out-of-range: {volume}")
            volume = clamp(volume, 0, 100)
        with pulse_monitor as pulse:
            self._set_volume(pulse, volume)

    @plugin.tag
    def get_volume(self):
        """Get the volume"""
        with pulse_monitor as pulse:
            volume = self._get_volume_and_mute(pulse)[0]
        return volume

    @plugin.tag
    def change_volume(self, step: int):
        """Increase/decrease the volume by step for the currently active output"""
        with pulse_monitor as pulse:
            volume, mute = self._get_volume_and_mute(pulse)
            volume += step
            # We could be muted, but have a high volume level and
            # increase the volume by a small step would suddenly blast out the music
            if mute:
                volume = step
            if not 0 <= volume <= 100:
                logger.warning(f"change_volume: volume out-of-range: {volume}")
                volume = clamp(volume, 0, 100)
            self._set_volume(pulse, volume)

    @plugin.tag
    def get_mute(self):
        """Return mute status for the currently active output"""
        with pulse_monitor as pulse:
            mute = self._get_volume_and_mute(pulse)[1]
        return mute

    @plugin.tag
    def mute(self, mute=True):
        """Set mute status for the currently active output"""
        with pulse_monitor as pulse_inst:
            sink = pulse_inst.get_sink_by_name(pulse_inst.server_info().default_sink_name)
            pulse_inst.mute(sink, mute)
            self._publish_volume(pulse_inst)

    @plugin.tag
    def set_output(self, sink_index: int):
        """Set the active output (sink_index = 0: primary, 1: secondary)"""
        with pulse_monitor as pulse:
            sink_name = self._set_output(pulse, sink_index)
        return sink_name

    @plugin.tag
    def set_soft_max_volume(self, max_volume: int):
        """Limit the maximum volume to max_volume for the currently active output"""
        logger.debug(f"Set Max Volume = {max_volume}")
        if not 0 <= max_volume <= 100:
            logger.warning(f"set_max_volume: volume out-of-range: {max_volume}")
            return
        self._soft_max_volume = max_volume
        with pulse_monitor as pulse:
            current_volume, mute = self._get_volume_and_mute(pulse)
            if max_volume < current_volume:
                self._set_volume(pulse, max_volume)
        cfg.setn('pulse', 'soft_max_volume', value=max_volume)

    @plugin.tag
    def get_soft_max_volume(self):
        """Return the maximum volume limit for the currently active output"""
        return self._soft_max_volume

    def card_list(self) -> List[pulsectl.PulseCardInfo]:
        """Return the list of present sound card"""
        with pulse_monitor as pulse:
            cards = pulse.card_list()
        return cards


pulse_control: PulseVolumeControl
pulse_monitor: PulseMonitor


def parse_config() -> List[PulseAudioSinkClass]:
    global pulse_monitor

    # We get the current default sink, in case of corrupt configuration
    with pulse_monitor as pulse_inst:
        default_sink_name = pulse_inst.server_info().default_sink_name
        default_sink = pulse_inst.get_sink_by_name(default_sink_name)
        all_sinks = [x.name for x in pulse_inst.sink_list()]
    sink_list = []

    with cfg:
        key = 'primary'
        alias = cfg.setndefault('pulse', 'outputs', key, 'alias', value='Unset alias')
        volume_limit = cfg.setndefault('pulse', 'outputs', key, 'volume_limit', value=100)
        pulse_sink_name = cfg.getn('pulse', 'outputs', key, 'pulse_sink_name', default=None)
        if pulse_sink_name is None:
            pulse_sink_name = default_sink_name
            logger.warning("The primary audio output configuration is incomplete. "
                           f"Creating an entry from the current default sink '{default_sink}'")
            cfg.setn('pulse', 'outputs', key, 'pulse_sink_name', value=pulse_sink_name)
        if pulse_sink_name not in all_sinks:
            # No need to change sink here, set_output later falls back to default_sink
            # We just reset volume scaling to unsuspecting 100 %
            volume_limit = 100
            logger.error(f"Configured sink '{pulse_sink_name}' not available sinks '{all_sinks}!\n"
                         f"Using default sink '{default_sink_name}' as fallback\n"
                         f"Things like audio sink toggle and volume limit will not work as expected!\n"
                         f"Please run audio config tool: ./installation/components/setup_configure_audio.sh")

        sink_list.append(PulseAudioSinkClass(alias, pulse_sink_name, volume_limit))
        key = 'secondary'
        pulse_sink_name = cfg.getn('pulse', 'outputs', key, 'pulse_sink_name', default=None)
        # No need to check validity of pulse sink name: this could be a disconnected bluetooth device
        if pulse_sink_name is None:
            logger.info("Ignoring secondary audio output configuration because it is missing or incomplete")
        else:
            # Only need to get the configuration, if device is actually configured
            alias = cfg.setndefault('pulse', 'outputs', key, 'alias', value='Unset alias')
            volume_limit = cfg.setndefault('pulse', 'outputs', key, 'volume_limit', value=100)
            sink_list.append(PulseAudioSinkClass(alias, pulse_sink_name, volume_limit))
    return sink_list


@plugin.initialize
def initialize():
    global pulse_control
    global pulse_monitor
    pulse_monitor = PulseMonitor()
    pulse_monitor.toggle_on_connect = cfg.setndefault('pulse', 'toggle_on_connect', value=True)
    pulse_monitor.start()

    pulse_control = PulseVolumeControl(parse_config())


@plugin.finalize
def finalize():
    global pulse_control
    # Set default output and start-up volume
    # Note: PulseAudio may switch the sink automatically to a connecting bluetooth device depending on the loaded module
    # with name module-switch-on-connect. On Raspberry Pi OS Bullseye, this module is not part of the default configuration.
    # So, we shouldn't need to worry about it. Still, set output and startup volume close to each other
    # to minimize bluetooth connection in between
    global pulse_control
    pulse_control.set_output(0)
    startup_volume = cfg.getn('pulse', 'startup_volume', default=None)
    if startup_volume is not None:
        pulse_control.set_volume(startup_volume)
    else:
        pulse_control.publish_volume()
    plugin.register(pulse_control, package="volume", name="ctrl", replace=True)


@plugin.atexit
def atexit(**ignored_kwargs):
    global pulse_monitor
    pulse_monitor.stop()
    return pulse_monitor
