Mock Reader
-----------------

A fake reader using a TK GUI for development purposes

**place-capable**: yes

.. note:: When using Anaconda, the GUI will look horrible!
    That is because Anaconda's TK is compiled without FreeType support

    There is a very quick and very dirty
    `fix <https://stackoverflow.com/questions/47769187/make-anacondas-tkinter-aware-of-system-fonts-or-install-new-fonts-for-anaconda>`_.
    Replacing the tk lib in anacondas environment with the system libtk:

    .. code-block:: bash

        cd /path/to/anaconda3/envs/rpi/lib
        mv ./libtk8.6.so ./libtk8.6.so.bak
        ln -s /usr/lib/x86_64-linux-gnu/libtk8.6.so libtk8.6.so
