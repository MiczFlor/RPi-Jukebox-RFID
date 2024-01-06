# Generic NFCPy Reader

This module is based on the user space NFC reader library [nfcpy](https://nfcpy.readthedocs.io/en/latest/overview.html) ([on github](https://github.com/nfcpy/nfcpy)).
The link above also contains a list of [supported devices](https://nfcpy.readthedocs.io/en/latest/overview.html#supported-devices).

The goal of this module is to handle USB NFC devices, that don't have a HID-keyboard
driver, and thus cannot be used with the [genericusb](genericusb.md) module. 

> [!NOTE]
> Since nfcpy is a user-space library, it is required to supress the kernel from loading its driver.
> The setup will do this automatically, so make sure the device is connected
> before running the [RFID reader configuration tool](../coreapps.md#RFID-Reader).

# Configuration

By setting `rfid > readers > generic_nfcpy > config > device_path` you can override the
device location. For possible values see the `path` parameter in this [nfcpy documentation](https://nfcpy.readthedocs.io/en/latest/modules/clf.html#nfc.clf.ContactlessFrontend.open)
