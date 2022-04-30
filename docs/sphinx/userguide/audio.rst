Audio Configuration
====================

The Jukebox supports 2 audio outputs, primary and secondary. The **primary output** is the default output and must
be available after system boot. This will typically be your sound card or the Pi's built-in headphone output.

The **secondary output** is an optional alternative output where the audio stream can be routed to.
Stream transfer happens on user input or automatically on the connection of an audio device.
This is mainly targeted at Bluetooth Headsets/Speakers.

Audio outputs run via PulseAudio and the basic configuration should be easy.
There is a :ref:`configuration tool<developer/coreapps:run_configure_audio.py>`,
to setup the configuration for the Jukebox Core App.

To set up the audio

    #. Follow the setup steps according to your sound card
    #. Check that the sound output works :ref:`as described below<userguide/audio:Checking system sound output>`
    #. Run the the tool :ref:`developer/coreapps:run_configure_audio.py`
    #. :ref:`Fine-tune audio parameters<userguide/audio:Additional options>`

Checking system sound output
-------------------------------

Run the following steps in a console:

.. code-block:: bash

    # Check available PulseAudio sinks
    $ pactl list sinks short
    0	alsa_output.platform-soc_sound.stereo-fallback  module-alsa-card.c	    s16le 2ch 48000Hz
    1	bluez_sink.C4_FB_20_63_CO_FE.a2dp_sink	        module-bluez5-device.c	s16le 2ch 44100Hz

    # Set the default sink (this will be reset at reboot)
    $ pactl set-default-sink sink_name

    # Check default sink is correctly set
    $ pactl info
    ....
    # Check volume level (exit with ESC)
    $ alsamixer

    # Play a sound
    $ paplay /usr/share/sounds/alsa/Front_Center.wav

    # This must also work when using an ALSA device
    $ aplay /usr/share/sounds/alsa/Front_Center.wav

You can also try different PulseAudio sinks without setting the default sink. In this case the volume is the last used
volume level for this sink:

.. code-block:: bash

    $ paplay -d sink_name /usr/share/sounds/alsa/Front_Center.wav


Bluetooth
-----------

Bluetooth setup consists of three steps

    #. Pair and connect your Bluetooth device
    #. Check the output works
    #. Re-run the config tool

To pair and connect, follow these steps. This will be a one-time setup.

.. code-block:: bash

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


Wait for a few seconds and then with ``$ pactl list sinks short``, check wether the Bluetooth device shows up as an output.
Its name usually looks like this: ``bluez_sink.C4_FB_20_63_CO_FE.a2dp_sink``.

Run through steps in `Checking system sound output` to check wether the output is working or not.
If it does not work immediately, turn your headset off and on to force a reconnect.

Rerun the config tool to register the Bluetooth device with the Jukebox core app as its secondary audio output.

Additional options
-------------------

For other audio configuration options, please look at the ``jukebox.yaml`` for now.

Directly edit ``jukebox.yaml`` following the steps: :ref:`userguide/configuration:Best practice procedure`.


Developer Information
-----------------------

The optional processing stages *Equalizer* and *Mono down mix* are realized by PulseAudio plugins.
The processing chain is

.. code-block:: text

    player --> mono mix --> equalizer --> hardware sink

Both plugins (if enabled) appear in the PulseAudio sinks

.. code-block:: bash

    $ pactl list sinks short
    ...

Which means we can put any of these as sink into the jukebox configuration file (if there is any need).

Mono down mix is enabled by the module ``module-remap-sink``
for which `documentation and an example can be found here
<https://www.freedesktop.org/wiki/Software/PulseAudio/Documentation/User/Modules/#module-remap-sink>`_.

The equalizer is the PulseAudio module ``module-ladspa-sink`` with the `corresponding documentation
<https://www.freedesktop.org/wiki/Software/PulseAudio/Documentation/User/Modules/#module-ladspa-sink>`_.

This in turn loads a `LADSPA plugin <https://www.ladspa.org/>`_.
The LADSPA plugin in the ``Eq10X2`` plugin of the `CAPS Library <http://quitte.de/dsp/caps.html#Eq10>`_
The CAPS library is available as linux package ``caps``.

This is the same plugin which is used in the
`equalizer for pure ALSA <https://github.com/raedwulf/alsaequal>`_
configurations which is part of the linux package ``libasound2-plugin-equal``.

You are, of course, free to modify the PulseAudio configuration to your needs. References

    #. `PulseAudio Documentation <https://www.freedesktop.org/wiki/Software/PulseAudio/Documentation/User>`_
    #. `PulseAudio Examples <https://wiki.archlinux.org/title/PulseAudio/Examples>`_

In this case, run the configuration tool with below parameter to avoid touching the PulseAudio configuration file.

.. code-block:: bash

    $ ./run_configure_audio.py --ro_pulse
