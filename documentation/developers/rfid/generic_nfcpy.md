# Generic NFCPy Reader

This module is based on the user space NFC reader library [nfcpy](https://nfcpy.readthedocs.io/en/latest/overview.html) ([on github](https://github.com/nfcpy/nfcpy)).
The link above also contains a list of supported devices.

The goal of this module is to handle USB NFC devices, that don't have a HID-keyboard
driver, and thus cannot be used with the [genericusb](genericusb.md) module. 

## Installation

Since nfcpy is a user-space library, it is required to supress the kernel from loading its driver:
	`echo 'install <DRIVER> /bin/true' > /etc/modprobe.d/disable_<DRIVER>.conf`

Where <DRIVER> is one of the following:
	- `pn533_usb` for PN531 PN532 and PN533 based devices connected via USB
	- `pn532_uart`\* for PN532 based devices connected via UART (or a UART-to-USB chip)
	- `port100`\* for Port100 based devices
	- `pn533_usb`\* for RC-S956 based devices

After the driver has been blacklisted. Unplug the device. Then either do `rmmod <DRIVER>`

[!NOTE]
\* Needs to be verified.

