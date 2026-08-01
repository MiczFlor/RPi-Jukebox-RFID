# Audio

## Configuration

The Jukebox supports 2 audio outputs, primary and secondary. The **primary output** is the default output and must
be available after system boot. This will typically be your sound card or the Pi's built-in headphone output.

The **secondary output** is an optional alternative output where the audio stream can be routed to.
Stream transfer happens on user input or automatically on the connection of an audio device.
This is mainly targeted at Bluetooth Headsets/Speakers.

Audio outputs run via PipeWire (with `wireplumber` as the session manager) and the basic configuration should be
easy. There is a [configuration tool](../developers/coreapps.md#Audio), to setup the configuration for the Jukebox
Core App.

### To set up the audio

1. Follow the setup steps according to your sound card
2. Check that the sound output works [as described below](audio.md#checking-system-sound-output)
3. Run the [audio configuration tool](../developers/coreapps.md#Audio)

#### Checking system sound output

Run the following steps in a console:

<!-- markdownlint-disable MD010 -->
```bash
# Check available audio sinks
$ wpctl status

# Set the default sink (id from `wpctl status`)
$ wpctl set-default <id>

# Check volume level (exit with ESC)
$ alsamixer

# Play a sound
$ pw-play /usr/share/sounds/alsa/Front_Center.wav

# This must also work when using an ALSA device
$ aplay /usr/share/sounds/alsa/Front_Center.wav
```
<!-- markdownlint-restore -->

You can also play a sound to a specific sink without changing the default. Use
the sink ID shown by `wpctl status`:

```bash
$ pw-play --target=<id> /usr/share/sounds/alsa/Front_Center.wav
```

## Bluetooth

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

If `bluetoothctl` has trouble to execute due to permission issue, try `sudo bluetoothctl`.

Wait for a few seconds and then with `$ wpctl status`, check whether the Bluetooth device shows up as an output.
The sink name usually looks like this: `bluez_output.C4_FB_20_63_CO_FE.1`.

Run through the steps above to check whether the output is working or not.
If it does not work immediately, turn your headset off and on to force a reconnect.

Rerun the config tool to register the Bluetooth device with the Jukebox core app as its secondary audio output.

## Additional options

For other audio configuration options, please look at the `jukebox.yaml` for now.

Directly edit `jukebox.yaml` following the steps: [Best practice procedure](configuration.md#best-practice-procedure).
