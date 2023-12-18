# Jukebox Configuration

The Jukebox configuration is managed by a set of files located in `shared/settings`.
Some configuration changes can be made through the WebUI and take immediate effect.

The majority of configuration options is only available by editing the config files -
*when the service is not running!*
Don't fear (overly), they contain commentaries.

For several aspects we have [configuration tools](../developers/coreapps.md#configuration-tools) and detailed guides:

* [Audio Configuration](./audio.md#audio-configuration)
* [RFID Reader Configuration](../developers/rfid/basics.md#reader-configuration)

Even after running the tools, certain aspects can only be changed by modifying the configuration files directly.

## Best practice procedure

```bash
# Make sure the Jukebox service is stopped
$ systemctl --user stop jukebox-daemon

# Edit the file(s)
$ nano ./shared/settings/jukebox.yaml

# Start Jukebox in console and check the log output (optional)
$ cd src/jukebox
$ ./run_jukebox.py 
# and if OK, press Ctrl-C and restart the service

# Restart the service
$ systemctl --user start jukebox-daemon
```

To try different configurations, you can start the Jukebox with a custom config file.
This could be useful if you want your Jukebox to only allow a lower volume when started
at night time when there is time to go to bed :-)

```bash
$ cd src/jukebox
$ ./run_jukebox.py --conf path/to/custom/config.yaml
```
