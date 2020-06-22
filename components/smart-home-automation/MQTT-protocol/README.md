
# Smart home integration using MQTT protocol

This module will integrate Phoniebox into a Smart Home environment and make it remotely controllable. It can be read out and controlled through MQTT which is widely supported in Smart Home environments. Several clients can connect to a MQTT server and exchange messages there just like in a chat room. Every MQTT client will publish messages and will also listen for messages. To make your Smart Home tool of choice talk to Phoniebox and vice versa both need to connect to a MQTT server that mostly comes with the Smart Home environment (e.g. [openHAB](https://openhab.org) comes with [Mosquitto](http://mosquitto.org/)). Phoniebox will automatically publish current status information periodically and in parallel listen for command messages from any MQTT client. Please refer to your Smart Home tool's documentation on how to setup MQTT for it. It will need to be able to listen for messages and also send messages to Phoniebox' "chat room" (=topic in MQTT terms).

# Use Cases

* let your Smart Home control Phoniebox based on time schedules
   * disable wifi in the evening when Phoniebox is used as a sleeping device
   * shutdown at night when it's finally bedtime
   * lower the volume in the mornings (to keep you asleep)
* control Phoniebox via Voice Assistants like [Snips](https://snips.ai) (which also uses MQTT!), Google Home, Amazon Echo,...
* let Phoniebox play an informational note to your kids that the weather outside is great and they should consider going outside (if your Smart Home has weather-based sensors)
* run statistics on when and how your kid uses Phoniebox
   * arrange terms with your kid how long the Phoniebox can be used (e.g. max. 2h per day)
   * monitor if your kid complies with those terms or enforce them if need be

# How it works
Phoniebox' MQTT client connects to the MQTT server that is defined in the `SETTINGS` section of the script itself. It is able to connect by authenticating...

1) with username and password
2) with server and client certificates

Please check your MQTT server configuration regarding which authentication method it is configured to use. Once connected to the MQTT server it will publish messages to the `mqttBaseTopic` that is defined in `SETTINGS` (defaults to `phoniebox`, we will use this default topic from now on on this page). Other MQTT clients that are e.g. part of a smart home solution can listen and respond to this base topic and its sub-topics.

Phoniebox' MQTT client will do the following things:

1. at startup send state and version info about Phoniebox to
   - `phoniebox/version` (e.g. 1.2-rc1)
   - `phoniebox/edition` (e.g. classic)
   - `phoniebox/state` (online)
   - `phoniebox/disk_total` (disk size in Gigabytes)
   - `phoniebox/disk_avail` (available disk size in Gigabytes)
2. at shutdown send state info to
   - `phoniebox/state` (offline)
3. periodically send *all* attributes to `phoniebox/attribute/$attributeName` (this interval can be defined through `refreshIntervalPlaying` and `refreshIntervalIdle` in the `SETTINGS` section)
4. listen for attribute requests on `phoniebox/get/$attribute`
5. listen for commands on `phoniebox/cmd/$command` (if a command needs a parameter it has to be provided via payload)

## Topic: phoniebox/get/$attribute
MQTT clients can (additionally to the periodic updates) request an attribute of Phoniebox. Sending an empty payload to `phoniebox/get/volume` will trigger Phoniebox' MQTT client to fetch the current volume from MPD and send the result to `phoniebox/attribute/volume`. 

### Possible attributes
- volume
- mute
- repeat
- random
- state
- file
- artist
- albumartist
- title
- album
- track
- elapsed
- duration
- trackdate
- last_card
- maxvolume
- volstep
- idletime
- rfid (status of rfid service [true/false])
- gpio (status of gpio service [true/false])
- remaining_stopafter [minutes left until "stop" is triggered]
- remaining_shutdownafter [minutes left until shutdown]
- remaining_idle [minutes left for the idle shutdown timer]

### Help
Sending empty payload to `phoniebox/get/help` will be responded by a list of all possible attributes to `phoniebox/available_attributes`

## Topic: phoniebox/cmd/$command
MQTT clients can send commands to Phoniebox. Sending an empty payload to `phoniebox/cmd/volumeup` will trigger Phoniebox' MQTT client to execute that command. If the command needs a parameter it has to be provided in the payload (e.g. for `setmaxvolume` a payload with the maximum volume is required).

### Possible commands
- volumeup
- volumedown
- mute
- playerplay
- playerpause
- playernext
- playerprev
- playerstop
- playerrewind
- playershuffle
- playerreplay
- scan
- shutdown
- shutdownsilent
- reboot
- disablewifi

### Possible commands (that require a parameter!)
- setvolume [0-100]
- setvolstep [0-100]
- setmaxvolume [0-100]
- setidletime [in minutes]
- playerseek [e.g. +20 for 20sec ahead or -12 for 12sec back]
- shutdownafter [in minutes; 0 = remove timer]
- playerstopafter [in minutes]
- playerrepeat [off / single / playlist]
- rfid [start / stop]
- gpio [start / stop]
- swipecard [card ID]
- playfolder [folder name (not path)]
- playfolderrecursive [folder name (not path)]

### Help
Sending empty payload to `phoniebox/cmd/help` will be responded by a list of all possible commands to `phoniebox/available_commands` and `phoniebox/available_commands_with_params`

# Installation

Install missing python packages for MQTT:

~~~
sudo pip3 install paho-mqtt
~~~

All relevant files can be found in the folder:

~~~
components/smart-home-automation/MQTT-protocol/
~~~

## Auto-Starting the daemon at bootup

* The daemon is run by executing the script `daemon-mqtt-client.py` which will run in an endless loop.
* There's a sample service file (`phoniebox-mqtt-client.service.stretch-default.sample`) that can be used to register the daemon to be run at bootup. 
* It is currently not integrated into the one-line-install script so please run the following commands to do it manually.

First step: copy files to destination locations:

~~~
# First copy the daemon script and service config file to the correct directory:
sudo cp /home/pi/RPi-Jukebox-RFID/components/smart-home-automation/MQTT-protocol/daemon-mqtt-client.py /home/pi/RPi-Jukebox-RFID/scripts/
sudo cp /home/pi/RPi-Jukebox-RFID/components/smart-home-automation/MQTT-protocol/phoniebox-mqtt-client.service.stretch-default.sample /etc/systemd/system/phoniebox-mqtt-client.service
~~~

Now edit the file `pi/RPi-Jukebox-RFID/scripts/daemon-mqtt-client.py` to match your requirements.
Now continue and activate the service.

~~~
# Now systemd has to be notified that there's a new service file:
sudo systemctl daemon-reload
# Now enable the service file, to start it on reboot:
sudo systemctl enable phoniebox-mqtt-client
# And now you can reboot to have your daemon running or start it manually:
sudo systemctl start phoniebox-mqtt-client
# To see if the reader process is running use the following command:
sudo systemctl status phoniebox-mqtt-client
~~~
