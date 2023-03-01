# Synchronize shared files from a server

This component activates a synchronisation from a server to the Phoniebox for the shared folders 'shortcuts' and 'audiofolders'.
This can be initiated as a "full-sync" command and optionally on every RFID scan for the particular CardID (and corresponding audiofolder).

For the "full-sync" bind a CardId to the command "SYNCSHAREDFULL".
For the "RFID scan sync" feature, activate the option in the configuration. There is also a command to toggle the activation of the "RFID scan sync" feature via CardId (bind to command "SYNCSHAREDONRFIDSCANTOGGLE").

## Synchronisation

The synchronisation will be FROM a server TO the Phoniebox, overriding existing files. So configuration of audiofiles / -folders made locally will be lost after sync.
If you want to make the initial setup e.g. via WebUi copy the files and use it as a base for the server.
The "folder.conf" files will be synced if present on the server, but not delete if not (they are automatically generated on playback).

To access the files on the server two modes are supported: SSH or MOUNT.
Please make sure you have the correct access rights for the source and use key-based authentication for SSH.

### RFID scan sync
If the feature "RFID scan sync" is activated, there will be a check on every RFID scan against the server if a matching shortcut and audiofolder is found and the changes will be transfered.
The playback will be delayed for the time the data are transfered (see "SYNCSHAREDFULL" to use a full-sync if a lot of new files have been added).
If the server is not reachable the check will be aborted after the timeout. So an unreachable server will cause a delay (see command "SYNCSHAREDONRFIDSCANTOGGLE" to toggle activation state). 
Deleted shortcuts / audiofolders (not the contained items) will not be purged locally if deleted on remote. This is also true for changed shortcuts (the old audiofolder / -files will remain). To also delete not existing items us a "full-sync".

## Installation

Run the 'install-sync-shared.sh' script. This will install all required packages and rights.
Please configure all settings according to your setup.


## Configuration

If your configuration has changed, run the script 'change_configuration.sh' to update the settings. This lets you also deactivate this feature.
You may also change the settings in the according files directly.

### Settings:

**{INSTALLATION_ROOT}/settings/sync-shared-enabled**

Holds the activation state of this feature. Values are "TRUE" or "FALSE"


**{INSTALLATION_ROOT}/settings/sync-shared.conf**

SYNCSHAREDMODE: The mode to access the server files. SSH or MOUNT

SYNCSHAREDREMOTESSHUSER: The username if SSH mode is used.

SYNCSHAREDREMOTESERVER: The IP or hostname of the server (used to check connectivity and SSH mode). e.g. "192.168.0.2" or "myhomeserver.local"

SYNCSHAREDREMOTEPORT: The port of the server (used to check connectivity and SSH mode). e.g. "80" or "22"

SYNCSHAREDREMOTETIMOUT: The timeout to reach the server (in seconds) (used to check connectivity). e.g. 1

SYNCSHAREDREMOTEPATH: The path to the shared files to sync (without trailing slash) (remote path for SSH mode or local path for MOUNT mode). e.g. "/mnt/Phoniebox"

SYNCSHAREDONRFIDSCAN: Holds the activation state of the optional feature "RFID scan sync". Values are "TRUE" or "FALSE"


## Special Thanks
inspired by [splitti - phoniebox_rsync](https://github.com/splitti/phoniebox_rsync)
