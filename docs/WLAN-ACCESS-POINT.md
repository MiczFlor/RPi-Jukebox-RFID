
# Access Phoniebox without Router

It is possible to connect to the Phoniebox directly, without having your
laptop and the Phoniebox connect to the same WiFi network. Configuring the
Raspberry Pi to be a WiFi access point.

I tested this only with the Raspberry Pi 3, which has a WiFi card onboard.
If you successfully did the same with another Raspberry Pi version, please
share your knowledge, I will weave it into the documenation. The reason I
say this is because creating a WiFi access point requires a WiFi card that
supports this mode. RPi3 does.

Install two packages we need later. Later meaning: when we might not have Internet anymore. Because the wlan0
interface will be set to a static IP
to create the access point.
```
sudo apt-get update
sudo apt-get install dnsmasq hostapd
```
## Configure the network

Using jessie, dhcpd is activated by default. This dhcp daemon is assigning
IP addresses to devices which want to connect to the Phoniebox.

Set the IP address for the wlan card by opening:
```
sudo nano /etc/network/interfaces
```
Replace the existing content with the following lines:
```
# Localhost
auto lo
iface lo inet loopback

# Ethernet
auto eth0
iface eth0 inet manual

# WLAN-Interface
allow-hotplug wlan0
iface wlan0 inet static
address 192.168.1.1
netmask 255.255.255.0
```
Now, the wlan is set to the IP address `192.168.1.1`.

We add one line to the dhcpd config file:
```
sudo nano /etc/dhcpcd.conf
```
Append the line:
```
denyinterfaces wlan0
```
Now we reboot and afterwards you should be connected to your RPi directly, not via ssh.
Because if your RPi relied on a WiFi connection to the Internet, this will be cut off.
Remember: we need the wlan0 interface to hook up other devices to a WiFi network the
RPi is creating.

Let's check if all interfaces are up and running. We only really need the wlan0
but if eth0 is also up and is connected to the Internet, your Phoniebox will be online
and all devices connected to it. Type in the command line:

```
ip a
```

This should list both interfaces (eth0 and wlan0). If it does, you can connect the RPi
to the Internet via an ethernet cable. But you still won't be able to connect to the
RPi via ssh quite yet. So make sure you have the RPi hooked up to a keyboard and a
monitor.

Reboot.

```
sudo reboot
```

## dhcp server configuration

```
sudo nano /etc/dnsmasq.conf
```
The following lines are the minimal configuration required.
```
# interface which is active
interface=wlan0

# interface to ignore
no-dhcp-interface=eth0

# IPv4 addresses and lease time
dhcp-range=192.168.1.100,192.168.1.200,24h

# DNS
dhcp-option=option:dns-server,192.168.1.1
```

Check the configuration before you start the dhcp server and
cache.
```
dnsmasq --test -C /etc/dnsmasq.conf
```
This should return 'OK'. Now start `dnsmasq`:
```
sudo systemctl restart dnsmasq
```
Check if it is up and running:
```
sudo systemctl status dnsmasq
```
Now install dnsmasq to start after boot:
```
sudo systemctl enable dnsmasq
```

## configure hostapd
To assign ssid and password, we need to configure
`hostapd`.
```
sudo nano /etc/hostapd/hostapd.conf
```
Replace the content of this file (if it already exists) with
the following content.
```
# interface and driver
interface=wlan0
#driver=nl80211

# WLAN-config
ssid=Phoniebox
channel=1
hw_mode=g
ieee80211n=1
ieee80211d=1
country_code=DE
wmm_enabled=1

# WLAN-encryption
auth_algs=1
wpa=2
wpa_key_mgmt=WPA-PSK
rsn_pairwise=CCMP
wpa_passphrase=Pl4yM3N0w
```
The network will be listed as `Phoniebox` and the password
to connect to the network is `Pl4yM3N0w` (as in 'play me now' with a number four and a number three and a zero). If you want a different ssid and/or password, edit the lines above.

This file contains a password in raw text, so make
sure only root can read it.
```
sudo chmod 600 /etc/hostapd/hostapd.conf
```
Check if this setup is correct. Open 
the wlan host in debug mode and read through the results.
```
sudo hostapd -dd /etc/hostapd/hostapd.conf
```
Scroll up to see if you can find these two lines anywhere:
```
wlan0: interface state COUNTRY_UPDATE->ENABLED
wlan0: AP-ENABLED 
```
If yes, you can also try to hook
up a device with the network already.
See if you can find `Phoniebox` as a WiFi network.

If that works, all is well. Stop the `hostapd` daemon with `Ctrl&C`.

Before we can start `hostapd` on boot, we have to add a few lines
in the config file to specify 
the location of the config file.
```
sudo nano /etc/default/hostapd
```
Add these lines:
```
RUN_DAEMON=yes
DAEMON_CONF="/etc/hostapd/hostapd.conf"
```
And start `hostapd` with the following commands:
```
sudo systemctl start hostapd
sudo systemctl enable hostapd
```
Check if the daemon is up and running:
```
sudo systemctl status hostapd
```
This concludes what we need to connect to the Phoniebox directly via WiFi.

If you plan to connect the `eth0` via a cable with the Internet, you need to learn about firewall configurations. Google how to do this (I hope to replace this last paragraph with a nicer explanation and a link later, when I find the time. Apologies.)

