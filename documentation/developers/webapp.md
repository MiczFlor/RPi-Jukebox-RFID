# Web App

The Web App sources located in `src/webapp`. During installation from the official repositories release branches a prebuilt bundle of the Web App is deployed. If you install a feature branch or from a fork repository the Web App needs to be build locally. This requires Node to be installed and is part of the installation process.

## Install node manually

If you installed an official release branch Node might not be installed (focus on builders). To add this for local development you can run the recommended setup (https://deb.nodesource.com/)

``` bash
sudo apt-get -y update && sudo apt-get -y install ca-certificates curl gnupg
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | sudo gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg
echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" | sudo tee /etc/apt/sources.list.d/nodesource.list
sudo apt-get -y update && sudo apt-get -y install nodejs
```

## Build the Web App

After changes to the Web App sources (locally or caused by a pull from the repository) it needs to be rebuild manually.
Use the provided script to rebuild whenever needed. The result is written to the folder `build`.
```

``` bash
cd ~/RPi-Jukebox-RFID/src/webapp; \
./run_rebuild.sh -u
```

## Known Issues while building

### JavaScript heap out of memory

While (re-) building the Web App, you get the following output:

``` {.bash emphasize-lines="12"}
> webapp@0.1.0 build
> react-scripts build

Creating an optimized production build...

[...]

<--- JS stacktrace --->

FATAL ERROR: Reached heap limit Allocation failed - JavaScript heap out of memory
```

#### Reason

Not enough memory for Node

#### Solution

Use the [provided script](#build-the-web-app) to rebuild the Web App. It sets the needed node options and also checks and adjusts the swap size if there is not enough memory available.

If you need to run the commands manually, make sure to have enough memory available (min. 512 MB). The following commands might help.

Set the swapsize to 512 MB (and deactivate swapfactor). Change accordingly if you have a SD Card with small capacity.
```bash
sudo dphys-swapfile swapoff
sudo sed -i "s|.*CONF_SWAPSIZE=.*|CONF_SWAPSIZE=512|g" /etc/dphys-swapfile 
sudo sed -i "s|^\s*CONF_SWAPFACTOR=|#CONF_SWAPFACTOR=|g" /etc/dphys-swapfile
sudo dphys-swapfile setup 
sudo dphys-swapfile swapon
```

Set the maximum amount of memory for node to use. Memory must be available.
``` bash
export NODE_OPTIONS=--max-old-space-size=512
npm run build
```

### Process exited too early // kill -9

``` {.bash emphasize-lines="8,9"}
> webapp@0.1.0 build
> react-scripts build

[...]

The build failed because the process exited too early.
This probably means the system ran out of memory or someone called 'kill -9' on the process.
```

#### Reason

Node tried to allocate more memory than available on the system.

#### Solution

See [JavaScript heap out of memory](#javascript-heap-out-of-memory)


### Client network socket disconnected

``` {.bash emphasize-lines="8,9"}
[...]

npm ERR! code ECONNRESET
npm ERR! network Client network socket disconnected before secure TLS connection was established
npm ERR! network This is a problem related to network connectivity.
npm ERR! network In most cases you are behind a proxy or have bad network settings.
npm ERR! network
npm ERR! network If you are behind a proxy, please make sure that the
npm ERR! network 'proxy' config is set properly.  See: 'npm help config'
```

#### Reason

The network connection is to slow or has issues. 
This can also happens on armv6l devices where the build takes significantly longer due to the limited resources. 

#### Solution

Try to use an ethernet connection. Also reboot might help. If the error still persists (or there is no ethernet port on your devices) try to raise the timeout for npm package resolution.

1. Check the current config value (default is 120000)
    ``` bash
    npm config --location project get fetch-retry-maxtimeout
    ```

1. Increase the value by '30000' (30 seconds) and set the new value
    ``` bash
    npm config --location project set fetch-retry-maxtimeout=xxx
    ```

1. Retry the build

