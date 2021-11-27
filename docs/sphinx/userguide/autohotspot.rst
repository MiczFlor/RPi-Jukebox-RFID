Auto-Hotspot
************

The Auto-Hotspot function allows the Jukebox to switch between its connection between a known WiFi and an automatically
generated hotspot so that you can still access via SSH or Webapp.

.. important:: Please configure the WiFi connection to your home access point before enabling these feature!

To create a hotspot and allow clients to connect `hostapd` [1]_ and `dnsmasq` [2]_

How to connect
--------------

When the Jukebox is not able to connect to a known WiFi it will create a hotspot named ``Phoniebox_Hotspot``. You will be
able to connect to this hotspot using the given password in the installation or the default password: ``PlayItLoud!``

Webapp
^^^^^^

After connecting to the ``Phoniebox_Hotspot`` you are able to connect to the webapp accessing the website `10.0.0.5 <http://10.0.0.5/>`_

ssh
^^^

After connecting to the ``Phoniebox_Hotspot`` you are able to connect via ssh to your Jukebox

.. code-block:: bash

    ssh pi@10.0.0.5


Changing basic configuration of the hotspot
-------------------------------------------

The whole hotspot configuration can be found at ``/etc/hostapd/hostapd.conf``.

The following parameters are relevant:

* ``ssid`` for the displayed hotspot name
* ``wpa_passphrase`` for the password of the hotspot
* ``country_code`` the country you are currently in

.. code-block:: bash

    $ cat /etc/hostapd/hostapd.conf

    #2.4GHz setup wifi 80211 b,g,n
    interface=wlan0
    driver=nl80211
    ssid=Phoniebox_Hotspot
    hw_mode=g
    channel=8
    wmm_enabled=0
    macaddr_acl=0
    auth_algs=1
    ignore_broadcast_ssid=0
    wpa=2
    wpa_passphrase==PlayItLoud!
    wpa_key_mgmt=WPA-PSK
    wpa_pairwise=CCMP TKIP
    rsn_pairwise=CCMP

    #80211n - Change GB to your WiFi country code
    country_code=DE
    ieee80211n=1
    ieee80211d=1

Disabling automatism
--------------------

Auto-Hotspot can be enabled or disabled using the Webapp.

.. important:: Disabling or enabling will keep the last state.

Troubleshooting
--------------------

Phoniebox is not connecting to the known WiFi
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The script will fall back to the hotspot so you still have some type of connection.

Check your password in ``/etc/wpa_supplicant/wpa_supplicant.conf``.

AutoHotspot functionality is not working
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can check the output of the script by running the following script:

.. code-block:: bash

    $ sudo /usr/bin/autohotspot

You need to add a new wifi network to the Raspberry Pi
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Because it is in Auto-Hotspot mode, you won't be able to scan for new wifi signals.

You will need to add a new network to ``/etc/wpa_supplicant/wpa_supplicant.conf`` manually. Enter the following details
replacing mySSID and myPassword with your details. If your WiFi has a hidden SSID then include the line ``scan_ssid=1``.

Resources
---------

`Raspberry Pi - Auto WiFi Hotspot Switch - Direct Connection <https://www.raspberryconnect.com/projects/65-raspberrypi-hotspot-accesspoints/158-raspberry-pi-auto-wifi-hotspot-switch-direct-connection>`__

------------

References:

.. [1] http://w1.fi/hostapd/
.. [2] https://thekelleys.org.uk/dnsmasq/doc.html
