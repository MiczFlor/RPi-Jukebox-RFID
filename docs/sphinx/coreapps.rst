.. Some helpful links
    https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html
    https://www.sphinx-doc.org/en/master/usage/extensions/index.html
    https://www.sphinx-doc.org/en/master/usage/extensions/autosectionlabel.html#module-sphinx.ext.autosectionlabel
    https://www.sphinx-doc.org/en/master/usage/restructuredtext/roles.html#ref-role
    https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-code-block
    https://pygments.org/docs/lexers/
    Python Directives:
    https://www.sphinx-doc.org/en/master/usage/restructuredtext/domains.html
    Content
    https://docutils.sourceforge.io/docs/ref/rst/directives.html#table-of-contents

Jukebox Core Apps
*****************

The Jukebox's core apps are located in ``src/jukebox``. Run the following command to learn more about each app and its parameters:

.. code-block:: bash

  $ ./run_app_name.py -h

run_jukebox.py
---------------

.. automodule:: run_jukebox

run_register_rfid_reader.py
-----------------------------

.. automodule:: run_register_rfid_reader

run_rpc_tool.py
---------------

.. automodule:: run_rpc_tool

run_publicity_sniffer.py
-------------------------

.. automodule:: run_publicity_sniffer

Configuration
**************

The Jukebox configuration is managed by set of files located in ``../shared/settings``.
Some configuration changes can be made through the WebUI and take immediate effect.

The majority of configuration options is only available by editing the config files.
Don't fear (overly), they contain commentaries.

Best practice procedure:

.. code-block:: bash

    # Make sure the Jukebox service is stopped
    $ sudo systemctl stop jukebox

    # Edit the file(s)
    $ nano ../shared/jukebox.yaml

    # Start Jukebox in console and check the log output (optional)
    $ ./run_jukebox.py
    # and if OK, press Ctrl-C and restart the service

    # Restart the service
    $ sudo systemctl start jukebox-daemon


To try different configurations, you can start the Jukebox with a custom config file. 
This could be useful if you want your Jukebox to only allow a lower volume when started
at night time when there is time to go to bed :-)

.. code-block:: bash

    $./run_jukebox.py --conf ../path/to/custom/config.yaml

Troubleshooting
*****************

We have made a point of providing extensive log messages.
In full debug mode, this may become very verbose. In fact, better observability
has been one of the design goals for version 3.

There are various options to get access to debug information.

The short answer
----------------

**We are still in the Pre-Release phase, so by default two log files should be written out:**

.. code-block:: bash

    ../shared/logs/app.log   : Complete Debug Messages
    ../shared/logs/errors.log: Only Errors and Warnings

.. important:: Always check the time modification date or the beginning of the log
    file to ensure you are not looking at an old log file!

The long answer: A few more details
------------------------------------

If started without parameters, the Jukebox checks for the existence of ``../shared/settings/logger.yaml``
and if present, uses that configuration for logging. This file is created by the installation process.
The default configuration file is also provided in ``../resources/default-settings/logger.default.yaml``.
We use Python's logging module to provide the debug messages which is configured through this file.

**We are still in the Pre-Release phase which means full debug logging is enabled by default.**

Default logging configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The default logging config does 2 things:

1. It writes 2 log files:

.. code-block:: bash

    ../shared/logs/app.log    : Complete Debug Messages
    ../shared/logs/errors.log : Only Errors and Warnings

2. Prints logging messages to the console. If run as a service, only error messages are emitted to console to avoid spamming the system log files.

Debug logging in console
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For debugging, it is usually very helpful to observe the apps output directly
on the console log.

.. code-block:: bash

    # Make sure the Jukebox service is stopped:
    $ sudo systemctl stop jukebox-daemon

    # Start the Jukebox in debug mode:
    # with default logger:
    $ ./run_jukebox.py

    # or with custom logger configuration:
    $ ./run_jukebox.py --logger ../path/to/logger.yaml

Fallback configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

It is possible to start the Jukebox with a catch-all debug enabler with a logger.yaml.
Attention: This only emits messages to the console and does not write to the log files!
This is more a fallback features:

.. code-block:: bash

    $./run_jukebox.py -vv

Extreme cases
^^^^^^^^^^^^^

Sometimes, the Jukebox app might crash with an exception and stack trace which is
neither logged, nor caught and handled.

If run locally from your console, you will see it immediately. No worries!

If running as a service, you will probably not even notice immediately that something has
gone pear-shaped. Services are restarted automatically when they fail.

Things are just not behaving as expected? Time to check the system logs:

.. code-block:: bash

    $journalctl -b -u jukebox-daemon
