# Update

## Updating your Jukebox Version 3

### Update from v3.2.1 and prior

As there are some significant changes in the installation, a new setup on a fresh image is required.

### General

Things on Version 3 are moving fast and you may want to keep up with recent changes. Since we are in Alpha Release stage,
a fair number of fixes are expected to be committed in the near future.

You will need to do three things to update your version from develop (or the next release candidate version)

1. Pull the newest code base from Github
2. Check for new entries in the configuration
3. Re-build the WebUI

```bash
# Switch to develop (if desired)
$ git checkout future3/develop

# Get latest code
$ git pull

# Check if new (mandatory) options appeared in jukebox.yaml
# with your favourite diff tool and merge them
$ diff shared/settings/jukebox.yaml resources/default-settings/jukebox.default.yaml

$ cd src/webapp
$ ./run_rebuild.sh
```

## Migration Path from Version 2

There is no update path coming from Version 2.x of the Jukebox.
You need to do a fresh install of Version 3 on a fresh Raspian Bullseye image.

> [!IMPORTANT]
> Do start with a fresh SD card image!

Do not just pull the future3 branch into you existing Version 2.x directory.
Do not run the installer on an system that had Version 2.x running before on it.
Stuff has changed too much to make this feasible.
