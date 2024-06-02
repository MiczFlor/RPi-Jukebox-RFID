# Web App

The Web App sources are located in `src/webapp`. A pre-build bundle of the Web App is deployed when installing from an official release branch. If you install from a feature branch or a fork repository, the Web App needs to be built locally. This requires Node to be installed and is part of the installation process.

## Install node manually

If you installed from an official release branch, Node might not be installed. To install Node for local development, follow the [official setup](https://deb.nodesource.com/).

``` bash
NODE_MAJOR=20
sudo apt-get -y update && sudo apt-get -y install ca-certificates curl gnupg
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | sudo gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg
echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" | sudo tee /etc/apt/sources.list.d/nodesource.list
sudo apt-get -y update && sudo apt-get -y install nodejs
```

## Develop the Web App

The Web App is a React application based on [Create React App](https://create-react-app.dev/). To start a development server, run the following command:

```bash
cd ~/RPi-Jukebox-RFID/src/webapp
npm install # Just the first time or when dependencies change
npm start
```

## Build the Web App

To build your Web App after its source code has changed (e.g. through a local change or through a pull from the repository), it needs to be rebuilt manually.
Use the provided script to rebuild whenever required. The artifacts can be found in the folder `build`.

```bash
cd ~/RPi-Jukebox-RFID/src/webapp; \
./run_rebuild.sh -u
```

After a successfull build you might need to restart the web server.

```bash
sudo systemctl restart nginx.service
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

Set the swapsize to 512 MB (and deactivate swapfactor). Adapt accordingly if you have a SD Card with small capacity.

```bash
sudo dphys-swapfile swapoff
sudo sed -i "s|.*CONF_SWAPSIZE=.*|CONF_SWAPSIZE=512|g" /etc/dphys-swapfile 
sudo sed -i "s|^\s*CONF_SWAPFACTOR=|#CONF_SWAPFACTOR=|g" /etc/dphys-swapfile
sudo dphys-swapfile setup 
sudo dphys-swapfile swapon
```

Set Node's maximum amount of memory. Memory must be available.

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

The network connection is too slow or has issues.
This tends to happen on `armv6l` devices where building takes significantly more time due to limited resources.

#### Solution

Try to use an ethernet connection. A reboot and/or running the script multiple times might also help ([Build produces EOF errors](#build-produces-eof-errors) might occur).

If the error still persists, try to raise the timeout for npm package resolution.

1. Open the npm config file in an editor
1. Increase the `fetch-retry-*` values by '30000' (30 seconds) and save
1. Retry the build

### Build produces EOF errors

#### Reason

A previous run failed during installation and left a package corrupted.

#### Solution

Remove the mode packages and rerun again the script.

``` {.bash emphasize-lines="8,9"}
rm -rf node_modules
```
