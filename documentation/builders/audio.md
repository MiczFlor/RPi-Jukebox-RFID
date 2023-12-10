# Audio

## Configuration

The Jukebox supports 2 audio outputs, primary and secondary. The **primary output** is the default output and must
be available after system boot. This will typically be your sound card or the Pi's built-in headphone output.

The **secondary output** is an optional alternative output where the audio stream can be routed to.
Stream transfer happens on user input or automatically on the connection of an audio device.
This is mainly targeted at Bluetooth Headsets/Speakers.

Audio outputs run via PulseAudio and the basic configuration should be easy.
There is a [configuration tool](../developers/coreapps.md#Audio),
to setup the configuration for the Jukebox Core App.

To set up the audio

1. Follow the setup steps according to your sound card
2. Check that the sound output works [as described below](audio.md#checking-system-sound-output)
3. Run the [audio configuration tool](../developers/coreapps.md#Audio)
4. [Fine-tune audio parameters](audio.md#additional-options)

## Checking system sound output

Run the following steps in a console:

```bash
# Check available PulseAudio sinks
$ pactl list sinks short
0	alsa_output.platform-soc_sound.stereo-fallback  module-alsa-card.c	    s16le 2ch 48000Hz
1	bluez_sink.C4_FB_20_63_CO_FE.a2dp_sink	        module-bluez5-device.c	s16le 2ch 44100Hz

# Set the default sink (this will be reset at reboot)
$ pactl set-default-sink <sink_name>

# Check default sink is correctly set
$ pactl info
....
# Check volume level (exit with ESC)
$ alsamixer

# Play a sound
$ paplay /usr/share/sounds/alsa/Front_Center.wav

# This must also work when using an ALSA device
$ aplay /usr/share/sounds/alsa/Front_Center.wav
```

You can also try different PulseAudio sinks without setting the default sink. In this case the volume is the last used
volume level for this sink:

```bash
$ paplay -d <sink_name> /usr/share/sounds/alsa/Front_Center.wav
```

# Bluetooth

Bluetooth setup consists of three steps

1. Pair and connect your Bluetooth device
2. Check the output works
3. Re-run the config tool

To pair and connect, follow these steps. This will be a one-time setup.

```bash
$ bluetoothctl
Agent registered
[CHG] Controller B8:27:EB:44:C4:33 Pairable: yes
#### Put your headset into pairing mode
[bluetooth]# scan on
Discovery started
#### Wait a few seconds for your device to appear
....
[NEW] Device C4:FB:20:63:CO:FE PowerLocus Buddy
....
[bluetooth]# scan off
....
[bluetooth]# pair C4:FB:20:63:CO:FE
....
Pairing successful
....
[bluetooth]# trust C4:FB:20:63:CO:FE
....
[bluetooth]# connect C4:FB:20:63:CO:FE
....
[PowerLocus Buddy]# exit
```

Wait for a few seconds and then with `$ pactl list sinks short`, check wether the Bluetooth device shows up as an output.
Its name usually looks like this: `bluez_sink.C4_FB_20_63_CO_FE.a2dp_sink`.

Run through steps above to check wether the output is working or not.
If it does not work immediately, turn your headset off and on to force a reconnect.

Rerun the config tool to register the Bluetooth device with the Jukebox core app as its secondary audio output.

## Additional options

For other audio configuration options, please look at the `jukebox.yaml` for now.

Directly edit `jukebox.yaml` following the steps: [Best practice procedure](configuration.md#best-practice-procedure).

## Developer Information

The optional processing stages *Equalizer* and *Mono down mix* are realized by PulseAudio plugins. The processing chain is

```
player --> mono mix --> equalizer --> hardware sink
```

Both plugins (if enabled) appear in the PulseAudio sinks

```bash
$ pactl list sinks short
```

Which means we can put any of these as sink into the jukebox configuration file (if there is any need).

Mono down mix is enabled by the module `module-remap-sink`
for which documentation and an example can be found [here](https://www.freedesktop.org/wiki/Software/PulseAudio/Documentation/User/Modules/#module-remap-sink).

The equalizer is the PulseAudio module `module-ladspa-sink` with the [corresponding documentation](https://www.freedesktop.org/wiki/Software/PulseAudio/Documentation/User/Modules/#module-ladspa-sink).

This in turn loads a [LADSPA plugin](https://www.ladspa.org/).
The LADSPA plugin in the `Eq10X2` plugin of the [CAPS Library](http://quitte.de/dsp/caps.html#Eq10). The CAPS library is available as linux package `caps`.

This is the same plugin which is used in the
[equalizer for pure ALSA](https://github.com/raedwulf/alsaequal)
configurations which is part of the linux package `libasound2-plugin-equal`.

You are, of course, free to modify the PulseAudio configuration to your needs. References

1. [PulseAudio Documentation](https://www.freedesktop.org/wiki/Software/PulseAudio/Documentation/User)
2. [PulseAudio Examples](https://wiki.archlinux.org/title/PulseAudio/Examples)

In this case, run the [audio configuration tool](../developers/coreapps.md#Audio) with the parameter `--ro_pulse` to avoid touching the PulseAudio configuration file.
