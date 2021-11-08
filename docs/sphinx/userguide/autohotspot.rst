AutoHotspot
***********

The AutoHotspoot function allows the phoniebox to switch between a connection to a known WiFi router and a automatically
generated hotspot, so that you can still access the phoniebox webapp or SSH directly to the phoniebox.

.. important:: Please configure the WiFi connection to your home access point before enabling these feature!

To create a hotspot and allow clients to connect `hostapd` [1]_ and `dnsmasq` [2]_

Changing basic configuration of the Hotspot
-------------------------------------------
The whole hotspot configuration can be found at ``/etc/hostapd/hostapd.conf``

Interesting for you might be:

* ``ssid`` for the displayed hotspot-name
* ``wpa_passphrase`` for the password of the hotspot
* ``country_code`` if you are located in another counry than Germany

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
Autohotspot can be enabled/disabled within the phoniebox webapp.

.. important:: Disabling or enabling will keep the last state.

Troubleshooting
--------------------
Phoniebox is not connecting to the known WiFi
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The script will fall back to the hotspot so you still have some type of connection.

Check your password in ``/etc/wpa_supplicant/wpa_supplicant.conf``.

AutoHotspot functionality is not working
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
You can check the output of the script by running

.. code-block:: bash

    $ sudo /usr/bin/autohotspot

You need to add a new wifi network to the RPi
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
But it is in Hotspot mode so you are unable to scan for new wifi signals.

You will need to add the new network to ``/etc/wpa_supplicant/wpa_supplicant.conf`` manually. Enter the following details
replacing mySSID and myPassword with the correct details. If your router has a hidden SSID/not Broadcast then include
the line `scan_ssid=1`

Resources
---------
Transferred the installation routine and functionality from the following tutorial into the phoniebox environment:

`Raspberry Pi - Auto WiFi Hotspot Switch - Direct Connection <https://www.raspberryconnect.com/projects/65-raspberrypi-hotspot-accesspoints/158-raspberry-pi-auto-wifi-hotspot-switch-direct-connection>`__

------------

References:

.. [1] http://w1.fi/hostapd/
.. [2] https://thekelleys.org.uk/dnsmasq/doc.html
