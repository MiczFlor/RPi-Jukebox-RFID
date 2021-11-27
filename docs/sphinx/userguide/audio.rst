Audio Configuration
====================

The JukeBox supports two audio outputs, primary and secondary. The **primary output** is the default output and must
be available after system boot. As such it typically is your sound card or the Pi's built-in headphone output.

The **secondary output** is an optional, alternative output the audio stream can be routed to.
Stream transfer happens on user input or automatically on the connection of an audio device.
This targeted at Bluetooth Headsets/Speakers.

Audio output runs via PulseAudio and basic configuration should be easy.
There is a :ref:`configuration tool<developer/coreapps:run_configure_audio.py>`,
to setup the configuration for the Jukebox Core App.

To set up the audio

    #. follow the setup steps according to your sound card
    #. check that the sound output works :ref:`as described below<userguide/audio:Checking system sound output>`
    #. run the the tool :ref:`developer/coreapps:run_configure_audio.py`
    #. :ref:`fine-tune audio parameters<userguide/audio:Additional options>`

Checking system sound output
-------------------------------

Run through the following steps in a console:

.. code-block:: bash

    # Check available pulse audio sinks
    $ pactl list sinks short
    0	alsa_output.platform-soc_sound.stereo-fallback  module-alsa-card.c	    s16le 2ch 48000Hz
    1	bluez_sink.C4_FB_20_63_CO_FE.a2dp_sink	        module-bluez5-device.c	s16le 2ch 44100Hz

    # Set the default sink (this will be reset at reboot)
    $ pactl set-default-sink sink_name
    # Check default sink is correctly set
    $ pactl info
    ....
    # Check volume level
    $ alsamixer
    # Play a sound
    $ paplay /usr/share/sounds/alsa/Front_Center.way
    # This must also work when using an ALSA device
    $ aplay /usr/share/sounds/alsa/Front_Center.way

You can also try different PulseAudio sinks without setting the default sink. In this case the volume is the last used
volume level for this sink:

.. code-block:: bash

    $ paplay -d sink_name /usr/share/sounds/alsa/Front_Center.way


Bluetooth
-----------

Bluetooth setup consists of three steps

    #. Pair and connect your bluetooth device
    #. Check the output works
    #. Re-run the config tool

For pair and connect follow these steps. Only needs to be done once.

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


Wait a few seconds, then check with ``$ pactl list sinks short`` the bluetooth device is there as output.
It usually it's name looks like ``bluez_sink.C4_FB_20_63_CO_FE.a2dp_sink``.

Run through step in `Checking system sound output` to check output is working.
If it does not work immediately, turn your headset off and on to force a re-connect.

Re-run the config tool to register the bluetooth device with the Jukebox Core App as secondary audio output.

Additional options
-------------------

For now, please look at the ``jukebox.yaml`` for more configuration options regarding the audio outputs.

Directly edit ``jukebox.yaml`` following the steps in
:ref:`userguide/configuration:Best practice procedure`.