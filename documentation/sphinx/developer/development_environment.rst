Development Environment
************************

You have 3 development options:

.. contents::

Directly on Raspberry Pi
------------------------

The full setup is running on the RPi and you access files via SSH. Pretty easy to set up as
you simply do a normal install and switch to the ``future3/develop`` branch.

Steps to install
````````````````

We recommend to use at least a Pi 3 or Pi Zero 2 for development. This hardware won't be needed
in production, but it can be slow while developing.

1. Install the latest Pi OS on a SD card.
2. Boot up your Raspberry Pi.
3. :ref:`Install <install:Install Phoniebox software>` the Jukebox software as if you were building a Phoniebox. You can install from your own fork and feature branch if you wish which can be changed later as well. The original repository will be set as ``upstream``.
4. Once the installation has successfully ran, reboot your Pi.
5. Due to some resource constraints, the Webapp does not build the latest changes and instead consumes the latest official release. To change that, you need to install NodeJS and build the Webapp locally.
6. Install NodeJS using the existing installer

.. code-block:: bash

    cd ~/RPi-Jukebox-RFID/installation/routines; \
    source setup_jukebox_webapp.sh; \
    _jukebox_webapp_install_node

7. To free up RAM, reboot your Pi.
8. Build the Webapp using the existing build command. If the build fails, you might have forgotten to reboot.

.. code-block:: bash

    cd ~/RPi-Jukebox-RFID/src/webapp; \
    ./run_rebuild.sh -u

9. The Webapp should now be updated.
10. To continuously  update Webapp, pull the latest changes from your repository and rerun the command above.


Locally on any Linux machine
------------------------------

The jukebox also runs on any Linux machine. The Raspberry Pi specific stuff will not work of course. That is no issue depending
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
