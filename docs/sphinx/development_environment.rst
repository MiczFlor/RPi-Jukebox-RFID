Development Environment
************************

You have 3 development options:

.. contents::

Directly on Raspberry Pi
------------------------

The full setup is running on the RPi and you access files via SSH. Pretty easy to set up as
you simply do a normal install and switch to the ``future3/develop`` branch.

Locally on any Linux machine
------------------------------

The jukebox also runs on any Linux machine. The RPi-specific stuff will not work of course. That is no issue depending
our your development area. USB RFID Readers, however, will work.
You may setup a Python virtual environment or a conda virtual environment. You will to install and execute `MPD (Music Player Daemon) <https://www.musicpd.org/>`_.

You will have to start MPD, Jukebox core application and the WebUI separately.

Using Docker container
------------------------------

There is a complete setup :ref:`docker workflow <docker:Phoniebox Development Runbook for Docker environments>`.

.. toctree::
    :hidden:

    docker
