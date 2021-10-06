Development Environment
************************

You have three options for development options:

.. contents::

Directly on RPi
---------------------

The full setup is running on the RPi and you access files via with remote access. Pretty easy to set up as
you simply do a normal install and switch to the future3/develop branch.

Locally on any Linux machine
------------------------------

The jukebox also runs on any Linux machine. The RPi-specific stuff will not work of course. That is no issue depending
our your development area. USB RFID Readers, however, will work.
You may setup a Python virtual environment or a conda virtual environment. You need an installed and running MPD.

If you start the web-server or work just with the core app is up too you.

Using Docker container
------------------------------

There is a fully setup :ref:`docker workflow <docker:Phoniebox Development Runbook for Docker environments>`.

.. toctree::
    :hidden:

    docker
