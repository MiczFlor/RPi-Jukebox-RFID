# Synchronisation RFID Cards

This component handles the synchronisation of RFID cards (audiofolder
and card database entries).

It allows to manage card database entries and audiofiles of one to many
Phonieboxes in a central place (e.g. NAS, primary Phoniebox etc.) in the
network, but allows to play the audio offline once the data has synced.
The synchronisation can be initiated with the command `sync-all` and
optionally on every RFID scan for a particular CardID and its
corresponding audiofolder. To execute the `sync-all` command, bind a
RFID card to the command. For the \"RFID scan sync\" feature, activate
the option in the configuration or bind a RFID card to the command for
dynamic activation or deactivation.

## Synchronisation

The synchronisation will be FROM a server TO the Phoniebox, overriding
existing files. A local configuration will be lost after the
synchronization. If you want to make the initial setup e.g. via WebUi
copy the files and use it as a base for the server.

To access the files on the server, 2 modes are supported: SSH or MOUNT.
Please make sure you have the correct access rights to the source and
use key-based authentication for SSH.

### RFID scan sync

If the feature \"RFID scan sync\" is activated, there will be a check on
every RFID scan against the server if a matching card entry and audiofolder is available. If so, changes will be synced. The playback
will be delayed for the time the data is transfered (see \"sync-all\" to
use a full synchronization if a lot of new files have been added). If
the server is not reachable, the check will be aborted after the
timeout. Therfore, an unreachable server will cause a delay (see
commands to toggle activation state). Deleted card entries /
audiofolders (not the contained items) will not be purged locally if
deleted on remote. This is also true for changed card entries (the old
audiofolder / -files will remain). To remove not existing items us a
\"sync-all\".

## Configuration

Set the corresponding setting in `shared\settings\jukebox.yaml` to
activate this feature.

``` yaml
modules:
    named:
        ...
        sync_rfidcards: synchronisation.rfidcards

...
sync_rfidcards:
    enable: false
    config_file: ../../shared/settings/sync_rfidcards.yaml
```

The settings file (`shared\settings\sync_rfidcards.yaml`) contains the
following configuration

``` yaml
sync_rfidcards:
    # Holds the activation state of the optional feature "RFID scan sync". Values are "TRUE" or "FALSE"
    on_rfid_scan_enabled: true # bool
    # Server Access mode. MOUNT or SSH
    mode: mount # 'mount' or 'ssh'
    credentials:
        # IP or hostname of the server (used to check connectivity and for SSH mode). e.g. "192.168.0.2" or "myhomeserver.local"
        server: ''
        # Port (used to check connectivity and for SSH mode). e.g. "80" or "22"
        port:  # int
        # Timeout to reach the server (in seconds) (used to check connectivity). e.g. 1
        timeout: 1 # int
        # Path to the shared files to sync (without trailing slash) (remote path for SSH mode or local path for MOUNT mode). e.g. "/mnt/Phoniebox"
        path: ''
        # Username if SSH mode is used.
        username: ''
```
