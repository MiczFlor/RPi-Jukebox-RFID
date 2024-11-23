# Jukebox Configuration

The Jukebox configuration is managed by a set of files located in `shared/settings`.
Some configuration changes can be made through the Web App and take immediate effect.

The majority of configuration options are only available by editing the config files -
*when the service is not running!*
Don't fear (overly), they contain commentaries.

For several aspects, we have [configuration tools](../developers/coreapps.md#configuration-tools) and [detailed guides](./README.md#features).

Even after using the tools, certain aspects can only be changed by directly modifying the configuration files.

## Best practice procedure

```bash
# Make sure the Jukebox service is stopped
$ systemctl --user stop jukebox-daemon

# Edit the file(s)
$ nano ./shared/settings/jukebox.yaml

# Start Jukebox in console and check the log output (optional)
$ ./run_jukebox.sh
# and if OK, press Ctrl-C and restart the service

# Restart the service
$ systemctl --user start jukebox-daemon
```

To try different configurations, you can start the Jukebox with a custom config file.
This could be useful if you want your Jukebox to only allow a lower volume when started
at nighttime, signaling it's time to go to bed. :-)
The path to the custom config file must be either absolute or relative to the folder `src/jukebox/`.

```bash
$ ./run_jukebox.sh --conf /absolute/path/to/custom/config.yaml
```
