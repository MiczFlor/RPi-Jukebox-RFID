# Synchronize shared files from a Server

This component activates a synchronisation from a server to the Phoniebox for the shared folders 'shortcuts' and 'audiofolders'.
This can be done with a full-sync as a special RFID command and optionally on every RFID scan for the particular CardID.

For the full-sync bind a CardId to the command "SYNCSHAREDFULL".
For the "RFID scan sync" feature, activate the option in the configuration. There is also a command to toggle the activation the RFID scan sync feature via CardId (bind to "SYNCSHAREDONRFIDSCANTOGGLE").

## Snynchronisation

The synchronisation will be FROM the server TO the Phoniebox, overriding existing files and settings. So configuration of audiofiles / -folders and CardIds made via WebUi will be lost after sync.
If you want to make the initial setup via WebUi copy the files and use it as a base for the server.
The "folder.conf" files will be synced if present on the server, but not delete if not (they are automatically generated on playback).

If the feature "RFID scan sync" is activated, there will be a check on every RFID scan against the server if a matching shortcut and audiofolder is found and the changes will be transfered.
If the server is not reachable the check will be aborted after the timeout. So an unreachable server will cause a delay (see command "SYNCSHAREDONRFIDSCANTOGGLE" to toggle activation state). 
Further will the playback be delayed for the time the data are transfered (see "SYNCSHAREDFULL" to use a full-sync if a lot of new files have been added).

To access the files on the server two modes are supported: SSH or MOUNT

## Installation

Run the 'install-sync-shared.sh' script. This will install all required packages and rights.
Please configure all settings according to your setup.


## Configuration

If your configuration has changed, run the script 'change_configuration.sh' to update the settings. This lets you also deactivate this feature.
You may also change the settings in the according files directly.

### Settings:

**INSTALLATION_ROOT/settings/Sync_Shared_Enabled**

Hold the activation state of this feature. Values are "TRUE" or "FALSE"


**INSTALLATION_ROOT/settings/sync_shared.conf**

SYNCSHAREDONRFIDSCAN: If the optional feature "RFID scan sync" is activated. Values are "TRUE" or "FALSE"

SYNCSHAREDREMOTESERVER: The IP or hostname of the server (used to check connectivity). e.g. "192.168.0.2" or "myhomeserver.local"

SYNCSHAREDREMOTEPORT: The port of the server (used to check connectivity). e.g. "80" or "22"

SYNCSHAREDREMOTEPATH: The path to the shared files to sync. e.g. "/mnt/Phoniebox"

SYNCSHAREDREMOTETIMOUT: The timeout to reach the server (in seconds) (used to check connectivity). e.g. 1

SYNCSHAREDMODE: The mode to access the server files. SSH or MOUNT

SYNCSHAREDREMOTESSHUSER: The username if SSH mode is used.