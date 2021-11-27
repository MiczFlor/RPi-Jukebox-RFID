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
You may setup a Python virtual environment or a conda virtual environment.
You will have to install and configure `MPD (Music Player Daemon) <https://www.musicpd.org/>`_.

In addition to the `requirements.txt`, you will this dependency. On the Raspberry PI, the latest stable
release of ZMQ does not support WebSockets. We need to compile the latest
version from Github, which is taken care of by the installation script.
For regular machines, the normal package can be installed:

.. code-block:: bash

    pip3 install pyzmq


You will have to start Jukebox core application and the WebUI separately. The MPD usually runs as a service.

Using Docker container
------------------------------

There is a complete setup :ref:`docker workflow <developer/docker:Phoniebox Development Runbook for Docker environments>`.

.. toctree::
    :hidden:

    docker
