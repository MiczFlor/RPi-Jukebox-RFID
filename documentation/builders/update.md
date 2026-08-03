# Update

- [Updating your Jukebox Version 3](#updating-your-jukebox-version-3)
  - [Manually upgrade to the latest version (not recommended)](#manually-upgrade-to-the-latest-version-not-recommended)
- [Migration Path from Version 2](#migration-path-from-version-2)

## Updating your Jukebox Version 3

Currently there is no functionality to update an existing installation to the next release.
This is planned for a future release ([#2304](https://github.com/MiczFlor/RPi-Jukebox-RFID/issues/2304))

To switch to the latest version

- back up your './shared' folder and changed files
- perform a new installation on a fresh image
- restore your backed up files after the new installation was successful
- check if new mandatory settings have been added

    ``` bash
    diff shared/settings/jukebox.yaml resources/default-settings/jukebox.default.yaml
    ```

### Manually upgrade to the latest version (not recommended)

> [!CAUTION]
> **This process is strongly discouraged to use in general.**
>
> It can help in some specific cases, like applying hotfixes on the `future3/main` branch or a few commits on the `future3/develop` branch.
This process may necessitate specific migration steps and, if overlooked, could result in system failure. Please use these steps with caution and note extra information in the release notes.

Typically these steps need to be considered

1. Backup local changes
1. Pull the latest changes and run update commands
1. Update Web App (if installed, and an official release branch is used)
1. Update the config files

#### In detail

1. Backup local changes

    - SSH into your Phoniebox and open the installation folder

        ```bash
        cd ~/RPi-Jukebox-RFID/
        ```

    - Stash your local changes:

        ```bash
        git stash push -m "Backup before pull"
        ```

    - Create a backup branch (and potentially delete an already existing one):

        ```bash
        git branch -D backup-before-pull
        git branch backup-before-pull
        ```

1. Pull the latest changes and run update commands:

    ```bash
    git pull
    ```

    After the `pull` some checks are triggered to make recommendations about needed update commands. Run the commands described in the output. If the Web App is installed, update it from the exact-commit bundle as described below.

    Note the commands in case of an backup restore.

1. Update Web App (if installed, and an official release branch is used):
    - Determine the required exact-commit bundle name:

        ```bash
        cd ~/RPi-Jukebox-RFID
        git rev-parse HEAD
        echo "webapp-build-$(git rev-parse --short=10 HEAD).tar.gz"
        ```

    - Go to the [GitHub Release page](https://github.com/MiczFlor/RPi-Jukebox-RFID/releases) for the branch used.
    - Under "Assets", find the bundle with exactly that name and copy its URL. If it is missing, stop and publish or rerun the `Test Build Web App v3` workflow for the commit. Do not use a bundle with a different commit suffix.
    - Backup the current Web App build:

        ```bash
        cd ~/RPi-Jukebox-RFID/src/webapp
        rm -rf build-backup
        mv build build-backup
        ```

    - On your Phoniebox, download and extract the bundle. Afterwards, delete the archive:

        ```bash
        cd ~/RPi-Jukebox-RFID/src/webapp
        bundle_name="webapp-build-$(git rev-parse --short=10 HEAD).tar.gz"
        wget "{URL}" -O "${bundle_name}"
        tar -xzf "${bundle_name}"
        rm -f "${bundle_name}"
        ```

1. Update the config files

    - Check if new mandatory settings have been added

        ``` bash
        diff shared/settings/jukebox.yaml resources/default-settings/jukebox.default.yaml
        ```

Reboot the Phoniebox:

   ```bash
   sudo reboot
   ```

Verify the version of your Phoniebox in the settings tab.

#### Revert to backup if needed

- SSH into your Phoniebox and open the installation folder

    ```bash
    cd ~/RPi-Jukebox-RFID/
    ```

- Reset current branch to the backup state:

    ```bash
    git reset --hard backup-before-pull
    ```

- Reapply stashed changes (if any):

    ```bash
    git stash pop
    ```

- Rerun noted update commands

- Revert Web App:

    ```bash
    cd ~/RPi-Jukebox-RFID/src/webapp
    rm -rf build
    mv build-backup build
    ```

## Migration path from Version 2

There is no update path coming from Version 2.x of the Jukebox.
You need to do a fresh install of Version 3 on a fresh Raspberry Pi OS image.
See [Installing Phoniebox future3](./installation.md).

> [!IMPORTANT]
> Do start with a fresh SD card image!

Do not just pull the future3 branch into you existing Version 2.x directory.
Do not run the installer on an system that had Version 2.x running before on it.
Stuff has changed too much to make this feasible.
