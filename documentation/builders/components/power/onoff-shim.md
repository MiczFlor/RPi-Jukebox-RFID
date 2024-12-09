# OnOff SHIM by Pimorino

The OnOff SHIM from Pimorino allows you to savely start and shutdown your Raspberry Pi through a button. While you can switch of your Phoniebox via an RFID Card (through an RPC command), it is difficult to switch it on again without cutting the physical power supply.

## Installation

To install the software, open a terminal and type the following command to run the one-line-installer. A reboot will be required once the installation is finished.

> [!NOTE]
> The installation will ask you a few questions. You can safely answer with the default response.

```bash
curl https://get.pimoroni.com/onoffshim | bash
```

* [Source](https://shop.pimoroni.com/products/onoff-shim?variant=41102600138)

## How to manually wire OnOff SHIM

The OnOff SHIM comes with a 12-PIN header which needs soldering. If you want to spare some GPIO pins for other purposes, you can individually wire the OnOff SHIM with the Raspberry Pi. Below you can find a table of Pins to be connected.

| Board pin name | Board pin | Physical RPi pin | RPi pin name |
|----------------|-----------|------------------|--------------|
| 3.3V           | 1         | 1, 17            | 3V3 power    |
| 5V             | 2         | 2                | 5V power     |
| 5V             | 4         | 4                | 5V power     |
| GND            | 6         | 6, 9, 20, 25     | Ground       |
| GPLCLK0        | 7         | 7                | GPIO4        |
| GPIO17         | 11        | 11               | GPIO17       |

* More information can be found here: <https://pinout.xyz/pinout/onoff_shim>

## Assembly options

![OnOffShim soldered on a Raspberry Pi](https://cdn.review-images.pimoroni.com/upload-b6276a310ccfbeae93a2d13ec19ab83b-1617096824.jpg?width=640)
