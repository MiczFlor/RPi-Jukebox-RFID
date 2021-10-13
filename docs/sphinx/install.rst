Installing Phoniebox future3
============================

Install Raspberry Pi OS Lite
-------------------------------------------

.. important:: Currently, the installation does only work on Raspberry Pi's with ARMv7 and ARMv8 architecture, so 2, 3 and 4!
    1 and Zero's will require a bit more work and are currently not supported!

Before you can install the Phoniebox software, you need to prepare your Raspberry Pi.

1. Connect a Micro SD card to your computer (preferable an SC card with high read throughput)
2. `Download <https://www.raspberrypi.org/software/>`_
   the `Raspberry Pi Imager <https://www.raspberrypi.org/blog/raspberry-pi-imager-imaging-utility/>`_ and open it
3. Select **Raspberry Pi OS Lite** (without desktop environment) as the operating system
4. Select your Micro SD card (your card will be formatted)
5. Click *Write*
6. Wait for the imaging process to be finished (it'll take a few minutes)


Initial Boot
-------------------------------------------

You will need a terminal, like PuTTY for Windows or the Terminal app for Mac to proceed with the next steps.

1. Open a terminal of your choice.
2. Insert your card again if it has been ejected automatically.
3. Navigate to your SC card e.g., ``cd /Volumes/boot`` for Mac or ``D:`` for Windows.
4. Enable SSH by adding a simple file.

    .. code-block:: bash

        $ touch ssh

5. Set up your Wifi connection.

    *Mac*

    .. code-block:: bash

        $ nano wpa_supplicant.conf

    *Windows*

    .. code-block:: bash

        D:\> notepad wpa_supplicant.conf

6. Insert the following content, update your country, Wifi credentials and save the file.

    .. code-block:: bash

        country=DE
        ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
        update_config=1

        network={
            ssid="network-name"
            psk="network-password"
        }

7. Eject your SD card and insert it into your Raspberry Pi.
8. Start your Raspberry Pi by attaching a power supply.
9. Login into your Raspberry Pi, username is ``pi`` and password is ``raspberry``.
   If ``raspberrypi.local`` does not work, find out your Raspberry Pi's IP address from your router.

Install Phoniebox software
-------------------------------------------

Run the following command in your SSH terminal and follow the instructions

.. code-block:: bash

    cd; bash <(wget -qO- https://raw.githubusercontent.com/MiczFlor/RPi-Jukebox-RFID/future3/develop/installation/install-jukebox.sh)
