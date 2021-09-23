# Jukebox Apps

You'll find the Jukebox's core apps here. To get help on parameters, on each app you may run

~~~
$./run_app_name.py -h
~~~

## run_jukebox.py

This is the main app and starts the Jukebox core. Usually this runs as a service, 
which is started automatically after boot-up. 

At times, it may be necessary to restart the service.
For example after a configuration change. Not all configuration changes can be applied on-the-fly. See [Configuration].

For debugging, it is usually desirable to run the Jukebox directly from the console rather than
as service. This gives direct logging info in the console and allows changing command line parameters.
See [Troubleshooting].

## run_rpc_tool.py

A command line tool for sending RPC commands to the running jukebox app. 
This uses the same interface as the WebUI. Can be used for additional control
or for debugging. 

The tool features auto-completion and command history. 

## run_publicity_sniffer.py

A command line tool that monitors all messages being sent out from the 
Jukebox via the publishing interface.  Received messages are printed in the console.
Mainly used for debugging.

# Configuration

The Jukebox configuration is contained in a set of files located in `../shared/settings`.
Some configuration changes can be made through the WebUI and take immediate effect.

The majority of configuration options is only available by editing the config files. 
Don't fear (overly), they contain commentaries.

Best practice procedure:
~~~
# Make sure the Jukebox service is stopped
$ sudo systemctl stop jukebox

# Edit the file(s)
$ nano ../shared/jukebox.yaml

# Start Jukebox in console and check the log output (optional) 
$ ./run_jukebox.py
# and if OK, press Ctrl-C and restart the service 

# Restart the service
$ sudo systemctl start jukebox-daemon
~~~

To try different configurations, you can start the Jukebox with a custom config file
~~~
$./run_jukebox.py --conf ../path/to/custom/config.yaml
~~~

# Troubleshooting

We have made a point of providing extensive log messages. 
In full debug mode, this may become very verbose. But, well, the more information, 
the better. In fact, better observability has been one of the design goals for Version 3. 

There are various options to get access to debug information.

### The short answer
We are still in the Pre-Release phase, so by default two log files should be written out:

~~~
../shared/logs/app.log   : Complete Debug Messages
../shared/logs/errors.log: Only Errors and Warnings
~~~

Important: Always check the time modification date or the beginning of the log
file to ensure you are not looking at an old log file!


### A few more details

If started without parameters, the Jukebox checks for the existence of `../shared/settings/logger.yaml`
and if present, uses that configuration for logging. This file is created by the installation process.
The default configuration file is also provided in `../ressources/default-settings/logger.default.yaml`.
We use Python's logging module to provide the debug messages which is configured through this file.

We are still in the Pre-Release phase which means full debug logging is enabled by default.

### Default logging configuration

The default logging config does two things

(1) Writes two log files:
~~~
../shared/logs/app.log   : Complete Debug Messages
../shared/logs/errors.log: Only Errors and Warnings
~~~

(2) Prints logging messages to the console. If run as a service only error messages are 
emitted to console in order not to spam the system log files.

#### Debug logging in console

For debugging, it is usually very helpful to observe the apps output directly 
on the console log.

Make sure the Jukebox service is stopped:
~~~
$sudo systemctl stop jukebox-daemon
~~~

Start the Jukebox in debug mode:
~~~
with default logger:
$./run_jukebox.py 

with custom logger configuration
$./run_jukebox.py --logger ../path/to/logger.yaml
~~~

#### Fallback configuration

Start the Jukebox with a catch-all debug enabler with a logger.yaml is possible. 
Attention: This only emits messages to console
and does not write the log files! This is more a fallback features. 
~~~
$./run_jukebox.py -vv
~~~

#### Extreme cases

Sometimes, the Jukebox App might crash with an Exception and Stack Trace which is 
neither logged, nor caught and handled. 

If run locally from your console, you will see this immediately. No worries!

If running as a service, you will probably not even notice immediately that something has
gone pear-shaped. Services are restarted automatically when the fail. 
Things are just not behaving as expected. Time to check the system logs:
~~~
$journalctl -b -u jukebox-daemon 
~~~




