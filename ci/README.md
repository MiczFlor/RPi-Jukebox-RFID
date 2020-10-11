# Docker Test-Environment

Having to re-flash the sd card of their raspberry pi did annoy ZyanKLee that much he created
this little set of tools to allow testing without flashing.

This is a work in progress so expect things to fail or being flaky.

## Howto

* First you need a raspberry pi with some decent performance (RPi 3 or 4 would be recommended)
* Flash its sd card with **raspbian buster lite**
* use raspi-config to resize the filesystem to the whole sd card (menu: 7 -> A1)
* install some tools and reboot:
```
      sudo apt-get update
      sudo apt-get -y dist-upgrade
      sudo apt-get -y install docker.io git
      sudo gpasswd -a pi docker
      sudo reboot
```
* login to your RPi
* clone this repo and cd into its local clone:
```
      git clone https://github.com/chbuehlmann/RPi-Jukebox-RFID.git
      cd /home/pi/RPi-Jukebox-RFID/
```
* build the docker image:
    * **on normal PCs:**
      ```
      docker build -t rpi-jukebox-rfid-stretch:latest -f ci/Dockerfile.stretch.amd64 .
      docker build -t rpi-jukebox-rfid-buster:latest -f ci/Dockerfile.buster.amd64 .
      ```

    * **on a raspberry pi:**
      ```
      docker build -t rpi-jukebox-rfid-stretch:latest -f ci/Dockerfile.stretch.armv7 .
      docker build -t rpi-jukebox-rfid-buster:latest -f ci/Dockerfile.buster.armv7 .
      ```
* get something to drink or eat
* run the freshly built docker image and start testing. For example:
    ```    
      docker run --rm -ti rpi-jukebox-rfid-buster:latest /bin/bash
      cd /home/pi/
      cp /code/scripts/installscripts/buster-install-default.sh /home/pi/
      bash buster-install-default.sh
    ```

    NOTE: Get familiar with docker and its flags - `--rm` for example will remove the
          container after you log out of it and all changes will be lost.


### mount hosts code as volume

The created image now contains all the code in the directory `/code` - if you do not want to
rebuild the image after each code-change you can 'mount' the RPi's code version into the
container:

```
    git clone https://github.com/chbuehlmann/RPi-Jukebox-RFID.git
    cd /home/pi/RPi-Jukebox-RFID/
    docker build -t rpi-jukebox-rfid-buster:latest -f ci/Dockerfile .
    docker run --rm -ti -w /code -v $PWD:/code rpi-jukebox-rfid-buster:latest /bin/bash

    cd /home/pi/
    cp /code/scripts/installscripts/buster-install-default.sh /home/pi/
    bash buster-install-default.sh
```

In that way every change to the code in the container will be available on the RPi as well as vice versa.
