# Generic NFCPy Reader

This module is based on the user space NFC reader library [nfcpy](https://nfcpy.readthedocs.io/en/latest/overview.html) ([on github](https://github.com/nfcpy/nfcpy)).
The link above also contains a list of [supported devices](https://nfcpy.readthedocs.io/en/latest/overview.html#supported-devices).

The goal of this module is to handle USB NFC devices, that don't have a HID-keyboard
driver, and thus cannot be used with the [genericusb](genericusb.md) module. Also some serial devices are supported.

> [!NOTE]
> Since nfcpy is a user-space library, it is required to supress the kernel from loading its driver.
> The setup will do this automatically, so make sure the device is connected
> before running the [RFID reader configuration tool](../coreapps.md#RFID-Reader).

## Configuration

The installation script will scan for compatible devices and will assist in configuration.
By setting `rfid > readers > generic_nfcpy > config > device_path` in `shared/settings/rfid.yaml` you can override the
device location. By specifying an explicit device location it is possible to use multiple readers compatible with NFCpy.

Example configuration for a usb-device with vendor ID 072f and product ID 2200:

```yaml
rfid:
  readers:
    read_00:
      module: generic_nfcpy
      config:
        device_path: usb:072f:2200
      same_id_delay: 1.0
      log_ignored_cards: false
      place_not_swipe:
        enabled: false
        card_removal_action:
          alias: pause
```

For possible values see the `path` parameter in this [nfcpy documentation](https://nfcpy.readthedocs.io/en/latest/modules/clf.html#nfc.clf.ContactlessFrontend.open)

## Non-Interactive Installation

During a non-interactive installation (see
[Non-Interactive Installation](../../builders/installation.md#non-interactive-installation)) the
device path is supplied via `RFID_READER_PARAMS`. For the example above
(`usb:072f:2200`) add these lines to your `install_config.env`:

```bash
ENABLE_RFID_READER=true
RFID_READER_MODULE=generic_nfcpy
RFID_READER_PARAMS="device_path=usb:072f:2200"
```

The installer then writes the `device_path` into the reader's `config` section
of `shared/settings/rfid.yaml` — no interactive device selection is needed.
When `RFID_READER_PARAMS` is omitted and exactly one NFC reader is connected,
the installer auto-detects and uses that device automatically.

The reader's dependencies are installed automatically as well
(`RFID_READER_DEPS=auto`, the default): the `nfcpy` Python package and the
driver/system setup from `setup.inc.sh` (kernel module blacklisting, udev
rules, user groups) so the reader is accessible without root. Set
`RFID_READER_DEPS=no` in `install_config.env` to skip this step.
