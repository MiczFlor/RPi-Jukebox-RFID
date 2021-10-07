Updating
**************

Updating your Jukebox Version 3
-------------------------------------

Things on Version 3 are moving fast and you may want to get stay on the edge. Since we are in Alpha Release stage,
a fair number of fixes are expected to be committed in the near future.

You will need to do three things to update your version from develop (or the next release candidate version)

#. Pull the newest code base from Github
#. Check for new entries in the configuration
#. Build the WebUI

.. code-block:: bash

    # Switch to develop (if desired)
    $ git checkout future3/develop

    # Get latest code
    $ git pull

    # Check if new (mandatory) options appeared in jukebox.yaml
    # with your favourite diff tool and merge them
    $ diff shared/settings/jukebox.yaml resources/default-settings/jukebox.default.yaml

    $ cd src/webapp

    # Optional: In rare cases you will need to update the npm dependencies
    # This is the case when the package.json changed
    $ npm install

    # Rebuild Web App
    $ npm run build


Migration Path from Version 2
-------------------------------------

There is no update path coming from Version 2.x of the Jukebox.
You will need to remove the 2.x Jukebox installation manually and then do a fresh install of Version 3.

.. note:: The recommended way is to start with a fresh SD card image.

If you do not want to wipe your SD card, follow this procedure:

#. Disable all Phoniebox services, reboot
#. Remove/Rename the current Phoniebox working directory
#. Run the :ref:`installer script <install:Install Phoniebox software>`

Do not just pull the future3 branch into you existing Version 2.x directory.
Stuff has changed too much to make this feasible.
