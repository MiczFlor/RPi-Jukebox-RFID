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

The full setup is running on the RPi and you access files via SSH.

### Steps to install

We recommend to use at least a Pi 3 or Pi Zero 2 for development. While this hardware won\'t be needed in production, it comes in helpful while developing.

1. Follow the [installation preperation](../builders/installation.md#install-raspberry-pi-os-lite) steps
1. [Install](../builders/installation.md#development) your feature/fork branch of the Jukebox software. The official repository will be set as `upstream`.
1. If neccessary [build the Web App](./webapp.md) locally

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
