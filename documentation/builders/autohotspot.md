# Auto-Hotspot

The Auto-Hotspot function allows the Jukebox to switch its connection between a known WiFi and an automatically generated hotspot so that you can still access via SSH or Web App.

> [!IMPORTANT]
> Please configure the WiFi connection to your home access point before enabling these feature!

## How to connect

When the Jukebox is not able to connect to a known WiFi it will automatically create a hotspot.
You will be able to connect to this hotspot using the password set in the installation.
After that you can access the Web App or connect via ssh like before using the IP from the configuration.

The default configuration is
``` text
* SSID              : Phoniebox_Hotspot_<hostname>
* Password          : PlayItLoud!
* WiFi Country Code : DE
* IP                : 10.0.0.1
```

## Disabling automatism

Auto-Hotspot can be enabled or disabled using the Web App or RPC Commands.

> [!NOTE]
> Disabling will run the wifi check again and keep the last connection state until reboot.

> [!IMPORTANT]
> If you disable this feature you will loose access to the Jukebox, if you are not near a known WiFi after reboot!

## Troubleshooting

### AutoHotspot functionality is not working

Check the autohotspot service status
``` bash
sudo systemctl status autohotspot.service
```

and logs
``` bash
sudo journalctl -u autohotspot.service -n 50
```

### Phoniebox is not connecting to the known WiFi

The script will fall back to the hotspot so you still have some type of
connection.

Check your wifi configuration.

### You need to add a new wifi network to the Raspberry Pi

#### Using the command line
Connect to the hotspot and open a terminal. Use the [raspi-config](https://www.raspberrypi.com/documentation/computers/configuration.html#wireless-lan) tool and add the new wifi.

## Resources

* [Raspberry Connect - Auto WiFi Hotspot Switch](https://www.raspberryconnect.com/projects/65-raspberrypi-hotspot-accesspoints/158-raspberry-pi-auto-wifi-hotspot-switch-direct-connection)
* [Raspberry Pi - Configuring networking](https://www.raspberrypi.com/documentation/computers/configuration.html#using-the-command-line)
* [dhcpcd / wpa_supplicant]()
    * [hostapd](http://w1.fi/hostapd/)
    * [dnsmasq](https://thekelleys.org.uk/dnsmasq/doc.html)
