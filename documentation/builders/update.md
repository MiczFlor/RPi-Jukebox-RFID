# Update

## Updating your Jukebox Version 3

### Update from v3.5.0 and prior

As there are some significant changes in the Jukebox installation, no updates can be performed with the installer.
Please backup your './shared' folder and changed files and run a new installation on a fresh image.
Restore your old files after the new installation was successful and check if new mandatory settings have been added.

``` bash
$ diff shared/settings/jukebox.yaml resources/default-settings/jukebox.default.yaml
```

## Manually upgrade to the latest version

> [!CAUTION]
> This documentation is only recommended for users running on `future3/develop` branch. For optimal system updates, it is strongly recommended to utilize the upgrade feature when transitioning to the next version (The Upgrade Feature will come in the future [#2304](https://github.com/MiczFlor/RPi-Jukebox-RFID/issues/2304)). Manual updates may necessitate specific migration steps and, if overlooked, could result in system failure. Please use these steps with caution.

If you only want to update a few recent commits, this following explanation outlines the steps to do so

Typically, 4 steps need to be considered

1. Backup Local Changes (Optional)
1. Pull the latest version from Github
1. Replace the Web App with the most recent build
1. Optional: Update the config files

### Fetch the most recent version from Github

First, SSH into your Phoniebox.

```bash
cd ~/RPi-Jukebox-RFID/
```

Second, get the latest version from Github. Depending on your proficiency with Git, you can also checkout a specific branch or version.
Be aware, in case you have made changes to the software, stash them to keep them safe.

1. Backup Local Changes (Optional):
    - Stash your local changes:

        ```bash
        git stash push -m "Backup before pull"
        ```

    - Create a Backup Branch (and potentially delete it in case it already exists):

        ```bash
        git branch -D backup-before-pull
        git branch backup-before-pull
        ```

1. Pull Latest Changes:

   ```bash
   git pull
   ```

1. Update Web App:
    1. Backup the current webapp build

        ```bash
        cd ~/RPi-Jukebox-RFID/src/webapp
        rm -rf build-backup
        mv build build-backup
        ```

    1. Go to the [Github Release page](https://github.com/MiczFlor/RPi-Jukebox-RFID/releases) find the latest `Pre-release` release (typically Alpha).
    1. Under "Assets", find the latest Web App release called "webapp-build-latest.tar.gz" and copy the URL.
    1. On your Phoniebox, download the file and extract the archive. Afterwards, delete the archive

        ```bash
        wget {URL}
        tar -xzf webapp-build-latest.tar.gz
        rm -rf webapp-build-latest.tar.gz
        ```

1. Reboot the Phoniebox:

   ```bash
   sudo reboot
   ```

1. Verify the version of your Phoniebox in the settings tab.

Revert to Backup If Needed:

- Checkout the backup branch:

    ```bash
    git checkout backup-before-pull
    ```

- Reapply stashed changes (if any):

    ```bash
    git stash pop
    ```

- Revert Web App:

    ```bash
    cd ~/RPi-Jukebox-RFID/src/webapp
    rm -rf build
    mv build-backup build
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
