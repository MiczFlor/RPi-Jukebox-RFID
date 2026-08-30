# Generic USB Reader

**place-capable**: typically no

This module covers all types of USB-based RFID input readers. If you
plan to connect multiple USB-based RFID readers to the Jukebox, make
sure to connect all of them before running the [RFID reader configuration tool](../coreapps.md#RFID-Reader).

> [!NOTE]
> This reader has **no fixed module defaults** because the input device must
> be identified. During a non-interactive setup the configuration tool
> auto-detects a uniquely connected keyboard-like device; if several
> candidates exist (or none), it aborts with a clear message instead of
> writing an unusable configuration. Supply the device explicitly to
> configure it without any prompts, e.g.
>
> ``` bash
> ./run_register_rfid_reader.py --reader generic_usb --deps auto --force \
>   --params 'device_name=KKMoon USB Keyboard'
> ```
>
> During a non-interactive installation set `RFID_READER_PARAMS` in the
> installer config file (see
> [Non-Interactive Installation](../../builders/installation.md#non-interactive-installation)).

The user running the Jukebox needs the required system permissions:

> [!NOTE]
> The user needs to be part of the group \'input\' for evdev to work. This should usually be the case. However, a user can be added with:
>
>``` bash
>sudo usermod -a -G input USER
>```
