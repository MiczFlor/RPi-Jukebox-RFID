# Samba

To conveniently copy files to your Phoniebox via network `samba` can be configured during the installation. The folder `./shared/` will be exposed as network share `phoniebox`, giving you access to the audio and config folders.

## Connect

To access the share open your OS network environment and select your Phoniebox device.
Alternatively directly access it via url with the file explorer (e.g. Windows `\\<ip-address-of-your-phoniebox>`, MacOS `smb://<ip-address-of-your-phoniebox>`).

See also

* [MacOS](https://support.apple.com/lt-lt/guide/mac-help/mchlp1140/mac)

## User name / Password

As login credentials use the same username you used to run the installation with. The password is `raspberry`.
You can change the password anytime using the command `sudo smbpasswd -a "<your-username>"`.
