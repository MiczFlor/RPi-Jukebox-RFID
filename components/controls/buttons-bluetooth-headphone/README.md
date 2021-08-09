## Contol Phoniebox via Buttons from Bluetooth Headset

Many bluetooth headsets or bluetooth speaker sets have buttons for controlling the music stream. **Let's make use of them!** 
This component provides support for controlling your Phoniebox through these buttons on your bluetooth headset (or speaker set).

### Installation

1. Make sure your bluetooth headset is connected to the Phoniebox. Follow the instructions in the [Wiki](https://github.com/MiczFlor/RPi-Jukebox-RFID/wiki/Bluetooth).
2. Execute `$ ./install-bt-buttons.sh. It will ask you to identify your headset and set up appropriate user rights, and registers the script as a service. It should work immediatly. In case of doubt, reboot.
	- If later changing the headset, re-run `$ ./register-device.py`. Reboot or restart the service with `sudo systemctl restart phoniebox-bt-buttons.service `

### Supported Buttons

Out-of-the box support is included for the following buttons

- Play/Pause
- Previous Track
- Next Track

Key codes are standarized and so it should also work with your headphones. If you want to add more keys or assign a different behaviour see [Troubleshooting](#troubleshooting)

*Note:* Volume up/down is inherently supported by the bluetooth protocol. There is no need to handle these by this script.

### On Connect / On Disconnect

If the feature [bluetooth-sink-switch](../../bluetooth-sink-switch) is enabled, the script automatically switches the audio stream to headphones / regular speakers on bluetooth connect / disconnect  respectivly. Playback state (play/pause) is retained.

*Note:* On-connect actions may take up to 4 seconds - please be patient (bluetooth connection is only checked every two seconds, bluetooth stream needs to be buffered, etc...)

You can **customize** the behaviour by editing the functions 

- `bt_on_connect(mpd_support=0)`
- `bt_on_disconnect(mpd_support=0)`

where `mpd_support` indicates wether the bt-sink-switch-feature is enabled.

### Troubleshooting

This feature has been tested with PowerLocus Buddy and Sennheiser Momentum M2 AEBT headphones.

#### Preparation

- Stop the service `$ sudo systemctl stop phoniebox-bt-buttons.service`
- Start the script in a command line with debug option `$ ./bt-buttons.py debug`

#### Check that correct bluetooth device is found

- Run the [preparatory steps](#preparation)
- Check headset is connected and listed as input event device with `$ cat /proc/bus/input/devices`. Note the device name.
- In the script's debug output you should see something like this. Here the MAC address is the device name
~~~
30.12.2020 21:44:41 - bt-buttons.py - DEBUG: bt_get_device_name() -> C4:FB:20:63:A7:F2
30.12.2020 21:45:05 - bt-buttons.py - DEBUG: bt_open_device(C4:FB:20:63:A7:F2): Device 'C4:FB:20:63:A7:F2' search success
30.12.2020 21:45:05 - bt-buttons.py - DEBUG: device /dev/input/event1, name "C4:FB:20:63:A7:F2", phys ""
~~~

- If you see discrepancies, re-run `$ ./register-device.py`(see above)

#### Add key codes / change actions
- Run the [preparatory steps](#preparation)
- Press the buttons on the headset and check for these debug outputs. Note down the keycode. The **163** is the keycode, you are looking for. Go through all the buttons. Also try short/long press. On my headphones, they result in different keycodes
```
30.12.2020 21:45:59 - bt-buttons.py - DEBUG: key event at 1609361159.529679, 163 (KEY_NEXTSONG), down
```
- Go into the source code and adjust these lines for desired behaviour
~~~python
                if event.code == bt_keycode_play:
                    proc = subprocess.run(f"{path}/../../../scripts/playout_controls.sh -c=playerpause", shell=True, check=False,
                                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                elif event.code == bt_keycode_pause:
                    proc = subprocess.run(f"{path}/../../../scripts/playout_controls.sh -c=playerpause", shell=True, check=False,
                                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

~~~

#### Still having trouble?
Check the basics: test the event input. Make sure the headphones are connected beforehand. Replace event*X* with the event number obtained from `$ cat /proc/bus/input/devices`. 

```$ cat /dev/input/eventX```

Press some buttons on the headset. Not all buttons will be forwarded, e.g. vol up/down may also be handled only in the headset.
 Try also long/short press. The output will look wired. Don't worry - the important thing is that you are seeing something on the console. Now go back to [Troubleshooting](#troubleshooting).