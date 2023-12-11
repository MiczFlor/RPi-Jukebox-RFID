
# Template Reader

*Template for creating and integrating a new RFID Reader*

> [!NOTE]
> For developers only

This template provides the skeleton API for a new Reader. If you follow
the conventions outlined below, your new reader will be picked up
automatically There is no extra need to register the reader module with
the Phoniebox. Just re-run [RFID reader configuration tool](../coreapps.md#RFID-Reader).

Follow the instructions in [template_new_reader.py](../../../src/jukebox/components/rfid/hardware/template_new_reader/template_new_reader.py)

Also have a look at the other reader subpackages to see how stuff works
with an example

## File structure

Your new reader is a python subpackage with these three mandatory files

``` bash
components/rfid/hardware/awesome_reader/
  +- awesome_reader.py  <-- The actual reader module
  +- description.py     <-- A description module w/o dependencies. Do not change the filename!
  +- README.rst         <-- The Readme
```

The module documentation must go into a separate file, called README.ME.

## Conventions

-   Single reader per directory / subpackage
-   reader module directory name and reader module file name must be
    identical
-   Obviously awesome_reader will be replaced with something more
    descriptive. The naming scheme for the subpackage is
    -   \<type_of_reader\>\_\<io_bus\>\_\<other_specials_like_special_lib\>
    -   e.g. generic_usb/generic_usb.py
    -   e.g. pn532_spi/pn532_spi.py
    -   ...
