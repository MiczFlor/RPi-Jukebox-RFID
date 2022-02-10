System Setup
=====================

A few words on how the system is setup and interacts.

The system consists of

    #. the :ref:`userguide/system:Music Player Daemon (MPD)` which we use for all music playback (local, stream, podcast, ...)
    #. the :ref:`userguide/system:PulseAudio` for flexible audio output support
    #. the :ref:`userguide/system:Jukebox Core Service` for controlling MPD and PulseAudio and providing all the features
    #. the :ref:`userguide/system:Web UI` which is served through an Nginx web server
    #. a set of :ref:`developer/coreapps:Configuration Tools` and
       a set of :ref:`developer/coreapps:Developer Tools`

.. note:: The default install puts everything into the folder ``/home/pi/RPi-Jukebox-RFID``.
    Another folder might work, but is certainly not tested. Things are installed for the default user ``pi``. Again,
    another user might work, but is not tested.

Music Player Daemon (MPD)
--------------------------

The Music Player Daemon runs as *user-local* service (not as system-wide service which is usually the default).
This is important for the interaction with PulseAudio.

You will find the MPD configuration file under

.. code-block:: text

    $HOME/.config/mpd/mpd.conf

All MPD *var*-files are also located in ``$HOME/.config/mpd``.

The service can be controlled with the *systemctl*-command when adding the parameter ``--user``:

.. code-block:: bash

    $ systemctl --user status mpd
    $ systemctl --user start mpd
    $ systemctl --user stop mpd

.. important:: Never start or enable the system-wide MPD service with `sudo systemctl start mpd`!

To check if MPD is running or has issues, use

.. code-block:: bash

    $ systemctl --user status mpd
    # or, if you need to get the full logs
    $ journalctl --user -b -u mpd

The ``systemd`` service file is located at the default location for user services:

.. code-block:: text

    /usr/lib/systemd/user/mpd.service

PulseAudio
---------------------

We use PulseAudio for the audio output configuration. Check out the Audio Configuration page for details.

The is a set of reasons:

    * It is easier to support and setup different audio hardware. Over the years, many builders have
      tried many different ways to set up audio on their Jukebox so this become the most reliable and compatible
      solution
    * We can cleanly control and switch between different audio outputs independent of the playback software
    * The current Pi OS based on Bullseye does not allow another way to control Bluetooth based speakers,
      as Bluealsa is currently not working with Bluez 5

The PulseAudio configuration file is located at

.. code-block:: text

    ~/.config/pulse/default.pa

Service control and service configuration file location is identical to MPD.

Jukebox Core Service
---------------------

The :ref:`developer/coreapps:Jukebox Core` runs as a *user-local* service with the name ``jukebox-daemon``.
Similar to MPD, it's important that it does run as system-wide service to be able to interact with PulseAudio.

The service can be controlled with the ``systemctl``-command by adding the parameter ``--user``

.. code-block:: bash

    $ systemctl --user start jukebox-daemon
    $ systemctl --user stop jukebox-daemon

Check out the service with

.. code-block:: bash

    $ systemctl --user status jukebox-daemon
    # and if you need to get the full log output
    $ journalctl --user -b -u jukebox-daemon

The ``systemd`` service file is located at the default location for user services:

.. code-block:: text

    /usr/lib/systemd/user/jukebox-daemon.service

Starting and stopping the service can be useful for debugging or configuration checks.

Web UI
-----------------------

The Web UI is served using nginx. Nginx runs as a system service. The home directory is localed at

.. code-block:: text

    /home/pi/RPi-Jukebox-RFID/src/webapp/build

The Nginx configuration is located at

.. code-block:: text

    /etc/nginx/sites-available/default
