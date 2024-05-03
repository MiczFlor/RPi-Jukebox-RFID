# HiFiBerry

The installation script works for the most common set of HiFiBerry boards but also other "DAC" related sound cards like `I2S PCM5102A DAC`.

## Automatic setup

Run the following command to install any HiFiBerry board. Make sure you reboot your device afterwards.

```bash
cd ~/RPi-Jukebox-RFID/installation/components
./setup_hifiberry.sh
```

If you know you HifiBerry Board identifier, you can run the script as a 1-liner as well

```bash
./setup_hifiberry.sh enable hifiberry-dac
```

If you like to disable your HiFiberry Sound card and enable onboard sound, run the following command

```bash
./setup_hifiberry.sh disable
```

## Additional information

If you like to understand what's happening under the hood, feel free to check the [install script](../../../../installation/components/setup_hifiberry.sh).

The setup is based on [HiFiBerry's instructions](https://www.hifiberry.com/docs/software/configuring-linux-3-18-x/).

## How to manually wire your HiFiBerry board

Most HiFiBerry boards come with 40-pin header that you can directly attach to your Pi. This idles many GPIO pins that may be required for other inputs to be attached (like GPIO buttons or RFID). You can also connect your HiFiBerry board separately. The following table show cases the pins required.

* [Raspberry Pi Pinout](https://github.com/raspberrypi/documentation/blob/develop/documentation/asciidoc/computers/os/using-gpio.adoc)

| Board pin name | Board pin | Physical RPi pin | RPi pin name |
|----------------|-----------|------------------|--------------|
| 3.3V           | 1         | 1, 17            | 3V3 power    |
| 5V             | 2         | 2, 4             | 5V power     |
| GND            | 6         | 6, 9, 20, 25     | Ground       |
| PCM_CLK        | 12        | 12               | GPIO18       |
| PCM_FS         | 36        | 36               | GPIO19       |
| PCM_DIN        | 38        | 38               | GPIO20       |
| PCM_DOUT       | 40        | 40               | GPIO21       |

You can find more information about manually wiring [here](https://forum-raspberrypi.de/forum/thread/44967-kein-ton-ueber-hifiberry-miniamp-am-rpi-4/?postID=401305#post401305).
