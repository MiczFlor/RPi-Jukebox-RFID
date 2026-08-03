# Samba

The Web App can upload files or complete folder trees, create folders, and
delete files or folders in the audio library. Samba is therefore optional and
disabled by default.

Enable Samba during installation when you want direct network access to the
complete `./shared/` directory. It is exposed as the `phoniebox` network share
and includes both the audio library and configuration files.

## Connect

To access the share open your OS network environment and select your Phoniebox device.
Alternatively directly access it via url with the file explorer (e.g. Windows `\\<ip-address-of-your-phoniebox>`, MacOS `smb://<ip-address-of-your-phoniebox>`).

See also

* [MacOS](https://support.apple.com/lt-lt/guide/mac-help/mchlp1140/mac)

## User name / Password

As login credentials use the same username you used to run the installation with. The password is `raspberry`.
You can change the password anytime using the command `sudo smbpasswd -a "<your-username>"`.
