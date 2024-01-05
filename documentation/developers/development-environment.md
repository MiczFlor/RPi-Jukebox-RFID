# Development Environment

You have 3 development options. Each option has its pros and cons. To interact with GPIO or other hardware, it's required to develop directly on a Raspberry Pi. For general development of Python code (Jukebox) or JavaScript (Web App), we recommend Docker. Developing on your local machine (Linux, Mac, Windows) works as well and requires all dependencies to be installed locally.

- [Development Environment](#development-environment)
  - [Develop in Docker](#develop-in-docker)
  - [Develop on Raspberry Pi](#develop-on-raspberry-pi)
    - [Steps to install](#steps-to-install)
  - [Develop on local machine](#develop-on-local-machine)
    - [Using WSL](#using-wsl)

## Develop in Docker

There is a complete [Docker setup](./docker.md).

## Develop on Raspberry Pi

The full setup is running on the RPi and you access files via SSH. Pretty easy to set up as you simply do a normal install and switch to the `future3/develop` branch.

### Steps to install

We recommend to use at least a Pi 3 or Pi Zero 2 for development. This hardware won\'t be needed in production, but it can be slow while developing.

1. Install the latest Pi OS on a SD card.
2. Boot up your Raspberry Pi.
3. [Install](../builders/installation.md) the Jukebox software as if you were building a Phoniebox. You can install from your own fork and feature branch you wish which can be changed later as well. The original repository will be set as `upstream`.
4. Once the installation has successfully ran, reboot your Pi.
5. Due to some resource constraints, the Web App does not build the latest changes and instead consumes the latest official release. To change that, you  need to install NodeJS and build the Web App locally.
6. Install NodeJS using the existing installer

    ``` bash
    cd ~/RPi-Jukebox-RFID/installation/routines; \
    source setup_jukebox_webapp.sh; \
    _jukebox_webapp_install_node
    ```

7. To free up RAM, reboot your Pi.
8. Build the Web App using the existing build command. If the build fails, you might have forgotten to reboot.

    ``` bash
    cd ~/RPi-Jukebox-RFID/src/webapp; \
    ./run_rebuild.sh -u
    ```

9. The Web App should now be updated.
10. To continuously update Web App, pull the latest changes from your repository and rerun the command above.

## Develop on local machine

The jukebox also runs on any Linux machine. The Raspberry Pi specific stuff will not work of course. That is no issue depending our your development area. USB RFID Readers, however, will work. You will have to install and configure [MPD (Music Player Daemon)](https://www.musicpd.org/).

In addition to the `requirements.txt`, you will this dependency. On the Raspberry PI, the latest stable release of ZMQ does not support WebSockets. We need to compile the latest version from Github, which is taken care of by the installation script. For regular machines, the normal package can be installed:

``` bash
pip install pyzmq
```

You will have to start Jukebox core application and the WebUI separately. The MPD usually runs as a service.

### Using WSL

You can also use WSL on Windows 10 or 11. This section describes how to use WSL with Visual Studio Code.

1. Install a Debian or Ubuntu image from Microsoft Store
2. Install the extension [Remote Explorer](https://marketplace.visualstudio.com/items?itemName=ms-vscode.remote-explorer) in Visual Studio Code
3. Select Remote Explorer
4. Select "WSL Targets"
5. Right-click on the previously installed WSL image and select "Connect in Current/New Window"
6. Follow the instructions from above
