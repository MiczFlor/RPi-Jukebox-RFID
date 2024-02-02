# Update

## Updating your Jukebox Version 3

### Update from v3.5.0 and prior

As there are some significant changes in the Jukebox installation, no updates can be performed with the installer.
Please backup your './shared' folder and changed files and run a new installation on a fresh image.
Restore your old files after the new installation was succefull and check if new mandatory settings have been added.

``` bash
$ diff shared/settings/jukebox.yaml resources/default-settings/jukebox.default.yaml
```

## Migration Path from Version 2

There is no update path coming from Version 2.x of the Jukebox.
You need to do a fresh install of Version 3 on a fresh Raspberry Pi OS image.
See [Installing Phoniebox future3](./installation.md).

> [!IMPORTANT]
> Do start with a fresh SD card image!

Do not just pull the future3 branch into you existing Version 2.x directory.
Do not run the installer on an system that had Version 2.x running before on it.
Stuff has changed too much to make this feasible.
