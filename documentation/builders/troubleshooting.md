# Troubleshooting

We have made a point of providing extensive log messages.
In full debug mode, this may become very verbose. In fact, better observability
has been one of the design goals for version 3.

There are various options to get access to debug information.

Debugging your setup runs in several steps

1. Check that [audio output works](audio.md#checking-system-sound-output)
2. Check that [MPD works](system.md#music-player-daemon-mpd)
3. Checking log messages from the Jukebox Core App as described below

## The short answer

```bash
shared/logs/app.log   : Complete Debug Messages
shared/logs/errors.log: Only Errors and Warnings
```

These files always contain the messages of the current run only.
The logs of previous runs are post-fixed with `.1`, e.g. `app.log.1`. This is useful for debugging issues during
shutdown of the service.

The logs are also available via the Web Server:

```
http://ip.of.your.box/logs
```

> [!IMPORTANT] Always check the time modification date or the beginning of the log file to ensure you are not looking at an old log file!

## The long answer: A few more details

If started without parameters, the Jukebox checks for the existence of `shared/settings/logger.yaml`
and if present, uses that configuration for logging. This file is created by the installation process.
The default configuration file is also provided in `resources/default-settings/logger.default.yaml`.
We use Python's logging module to provide the debug messages which is configured through this file.

**We are still in the Pre-Release phase which means full debug logging is enabled by default.**

### Default logging configuration

The default logging config does 2 things:

1. It writes 2 log files:

```bash
shared/logs/app.log    : Complete Debug Messages
shared/logs/errors.log : Only Errors and Warnings
```

2. Prints logging messages to the console. If run as a service, only error messages are emitted to console to avoid spamming the system log files.

### Debug logging in console

For debugging, it is usually very helpful to observe the apps output directly
on the console log.

``` bash
# Make sure the Jukebox service is stopped:
$ systemctl --user stop jukebox-daemon

# Start the Jukebox in debug mode:
$ cd src/jukebox

# with default logger:
$ ./run_jukebox.py
# or with custom logger configuration:
$ ./run_jukebox.py --logger path/to/custom/logger.yaml
```

### Fallback configuration

It is possible to start the Jukebox with a catch-all debug enabler with a logger.yaml.
Attention: This only emits messages to the console and does not write to the log files!
This is more a fallback features:

``` bash
$ cd src/jukebox
$ ./run_jukebox.py -vv
```

### Extreme cases

Sometimes, the Jukebox app might crash with an exception and stack trace which is
neither logged, nor caught and handled.

If run locally from your console, you will see it immediately. No worries!

If running as a service, you will probably not even notice immediately that something has
gone pear-shaped. Services are restarted automatically when they fail.

Things are just not behaving as expected? Time to check the system logs:

``` bash
$ journalctl --user -b -u jukebox-daemon
```
