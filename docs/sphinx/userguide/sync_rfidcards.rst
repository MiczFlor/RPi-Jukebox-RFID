Syncronisation RFID Cards
*************************

This components handles the synchronisation of RFID cards (audiofolder and card database entries).

It allows to manage the card database entries and audiofiles of one to many Phonieboxes
in a central place (e.g. NAS, one main Phoniebox, ...) in the network,
but keeps the possibility to play audio offline once the data where synced.
The synchronisation can be initiated as a "sync-all" command
and optionally on every RFID scan for the particular CardID (and corresponding audiofolder).
For the "sync-all" bind a cardId to the command.
For the "RFID scan sync" feature, activate the option in the configuration
or bind a cardId to the command for dynamic de-/activation.

Synchronisation
---------------

The synchronisation will be FROM a server TO the Phoniebox, overriding existing files.
So configuration made locally will be lost after sync.
If you want to make the initial setup e.g. via WebUi copy the files and use it as a base for the server.

To access the files on the server two modes are supported: SSH or MOUNT.
Please make sure you have the correct access rights for the source and use key-based authentication for SSH.

RFID scan sync
^^^^^^^^^^^^^^
If the feature "RFID scan sync" is activated, there will be a check on every RFID scan against the server
if a matching card entry and audiofolder is found and the changes will be transfered.
The playback will be delayed for the time the data are transfered (see "sync-all" to use a full-sync if a lot of new files have been added).
If the server is not reachable the check will be aborted after the timeout.
So an unreachable server will cause a delay (see commands to toggle activation state).
Deleted card entries / audiofolders (not the contained items) will not be purged locally if deleted on remote.
This is also true for changed card entries (the old audiofolder / -files will remain). To also delete not existing items us a "sync-all".

Configuration
-------------

To activate this feature set the corresponding setting in ``shared\settings\jukebox.yaml``

.. code-block:: yaml

    modules:
        named:
            ...
            sync_rfidcards: synchronisation.rfidcards

    ...
    sync_rfidcards:
        enable: false
        config_file: ../../shared/settings/sync_rfidcards.yaml

The settingsfile (``shared\settings\sync_rfidcards.yaml``) contains the following configuration

.. code-block:: yaml

    sync_rfidcards:
        # Holds the activation state of the optional feature "RFID scan sync". Values are "TRUE" or "FALSE"
        on_rfid_scan_enabled: true # bool
        # The mode to access the server files. SSH or MOUNT
        mode: mount # 'mount' or 'ssh'
        credentials:
            # The IP or hostname of the server (used to check connectivity and for SSH mode). e.g. "192.168.0.2" or "myhomeserver.local"
            server: ''
            # The port of the server (used to check connectivity and for SSH mode). e.g. "80" or "22"
            port:  # int
            # The timeout to reach the server (in seconds) (used to check connectivity). e.g. 1
            timeout: 1 # int
            # The path to the shared files to sync (without trailing slash) (remote path for SSH mode or local path for MOUNT mode). e.g. "/mnt/Phoniebox"
            path: ''
            # The username if SSH mode is used.
            username: ''
