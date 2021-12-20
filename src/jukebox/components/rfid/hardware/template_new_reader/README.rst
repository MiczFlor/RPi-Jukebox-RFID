Template Reader
----------------

Or in full: *Template for creating and integrating a new RFID Reader*

.. note:: For developers only

This template provides the skeleton API for a new Reader.
If you follow the conventions outlined below, your new reader will be picked up automatically
There is no extra need to register the reader module with the Phoniebox.
Just re-run :ref:`the reader config tool <developer/coreapps:run_register_rfid_reader.py>`.

Follow the instructions in `template_new_reader.py`

Also have a look at the other reader subpackages to see how stuff works with an example


File structure
^^^^^^^^^^^^^^^^^^^^

Your new reader is a python subpackage with these three mandatory files

.. code-block:: bash

  components/rfid/hardware/awesome_reader/
    +- awesome_reader.py  <-- The actual reader module
    +- description.py     <-- A description module w/o dependencies. Do not change the filename!
    +- README.rst         <-- The Readme

The module documentation must go into a separate file so we can import it into the Sphinx document generation flow
without loading the Python module.

Conventions
^^^^^^^^^^^^^^^^^^

* Single reader per directory / subpackage
* reader module directory name and reader module file name must be identical
* Obviously awesome_reader will be replaced with something more descriptive. The naming scheme for the subpackage is

  * <type_of_reader>_<io_bus>_<other_specials_like_special_lib>
  * e.g. generic_usb/generic_usb.py
  * e.g. pn532_spi/pn532_spi.py
  * ...
