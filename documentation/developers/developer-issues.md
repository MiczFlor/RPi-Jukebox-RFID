# Developer Issues

## Building the Webapp on the PI

### JavaScript heap out of memory

While (re-) building the Web App, you get the following output:

``` {.bash emphasize-lines="12"}
pi@MusicPi:~/RPi-Jukebox-RFID/src/webapp $ npm run build

> webapp@0.1.0 build
> react-scripts build

Creating an optimized production build...

[...]

<--- JS stacktrace --->

FATAL ERROR: Reached heap limit Allocation failed - JavaScript heap out of memory
```

**Reason**

Not enough memory for Node

**Solution**

Prior to building set the node memory environment variable.

1. Make sure the value is less than the total available space on the
    system, or you may run into the next issue. (Not always though!)
    Check memory availability with `free -mt`.
2. We also experience trouble, when the space is set too small a
    value. 512 always works, 256 sometimes does, sometimes does not.
    If your free memory is small, consider increasing the swap size of
    your system!

``` bash
export NODE_OPTIONS=--max-old-space-size=512
npm run build
```

Alternatively, use the provided script, which sets the variable for you
(provided your swap size is large enough):

``` bash
$ cd src/webapp
$ ./run_rebuild.sh
```

**Changing Swap Size**

This will set the swapsize to 1024 MB (and will deactivate swapfactor). Change accordingly if you have a SD Card with small capacity.

```
sudo dphys-swapfile swapoff
sudo sed -i "s|.*CONF_SWAPSIZE=.*|CONF_SWAPSIZE=1024|g" /etc/dphys-swapfile 
sudo sed -i "s|^\s*CONF_SWAPFACTOR=|#CONF_SWAPFACTOR=|g" /etc/dphys-swapfile
sudo dphys-swapfile setup 
sudo dphys-swapfile swapon
```

### Process exited too early // kill -9

``` {.bash emphasize-lines="8,9"}
pi@MusicPi:~/RPi-Jukebox-RFID/src/webapp $ npm run build

> webapp@0.1.0 build
> react-scripts build

...

The build failed because the process exited too early.
This probably means the system ran out of memory or someone called 'kill -9' on the process.
```

**Reason**

Node tried to allocate more memory than available on the system.

**Solution**

Adjust the node memory variable as described in [JavaScript heap out of memory](#javascript-heap-out-of-memory). But make sure to allocate less memory than the available memory. If that is not sufficient, increase the swap file size of your
system and try again.
