#!/usr/bin/env python3

from evdev import InputDevice, categorize, ecodes
from subprocess import check_call
import time

# Enable Bluetooth Headphone Buttons for Music Control
# Script will listen to headphone button press events and call approriate phonibox control function
# If no headset is connected, it will endlessly check headset connection status every 3 seconds.


# Step 1: Find out which event the bluetooth headset is connected to.
#   It will be an input event device: /dev/input/eventX
#   Make sure it is connected first and you can playback music :-) Follow the excellent instructions in the wiki
#
#   Option 1) cat /proc/bus/input/devices
#             In my case the bluetooth headset is listed under its MAC address           
#   Option 2) Disconnect headset, show >ls /dev/input
#             Connect headset   , show >ls /dev/input, analyze the difference
#
# Step 2: Test the event
#   > cat /dev/input/event1
#   Press some buttons on the headset. Not all buttons will be forwarded, e.g. vol up/down may also be handled only in the headset.
#   Try also long/short press
#   The output will look wired. Don't worry - the important thing is that you are seeing something on the console
#
# Step 3: Figure out the key mappings
#   In this script adapt the EVTDEV constant to fit your input event device
#   Call this script directly from command the line (make sure it does not run as a service, if you already used the install script: >sudo systemctl stop phoniebox-bt-buttons)
#     >./bt-buttons.py
#   Press a button on the headset. The script will output a log like this
#
#     key event at 1600886330.107993, 201 (KEY_PAUSECD), up
#
#   The "201" is the keycode, you are looking for. Go through all the buttons. Also try short/long press. On my headphones, they result in different keycodes
#
# Step 4: Adjust this script with keycodes (and behavior)
#   If you are only looking for the play/pause/next/prev, simply adapt the keycodes below
#   If you have more buttons than I have, you may extend the if-else clause towards the end of the script.
#   To add new ctrl functions, check out playout_controls.sh for available commands
#
# This script has been tested with the following headset: PowerLocus Buddy
#
# Note:
# (a) If the event device does not exist, this script will not throw an error. (You will see no output if things dont work!)
#     But continue checking if that event will appear at some time, i.e. which will happen if the headset gets connected.
#     So if nothing happens, make sure you have the right event device listed here. 
# (b) This script assumes a constant /dev/input/eventX to headset mapping, which is not globally given.
#     But in a stable raspberry pi setup it will be constant, if no input devices are added/removed (especially in any order)
#
# Possible future feature enhancements
#   Use cat /proc/bus/input/devices first to find correct eventX to headset mapping
#
# If you want this script to run automatically as service after booting do this:
#   The easy way:
#     run the install script
#   The hard way:
#     Adjust directory paths in phoniebox-bt-buttons.service.sample
#     sudo cp phoniebox-bt-buttons.service.sample /etc/systemd/system/phoniebox-bt-buttons.service
#     sudo chown root:root /etc/systemd/system/phoniebox-bt-buttons.service
#     sudo chmod 644 /etc/systemd/system/phoniebox-bt-buttons.service
#     sudo systemctl enable phoniebox-bt-buttons.service
#
# Troubleshooting
#   If buttons fail to work after reboot, take a look into the boot messages to analyze the service messages
#     >journalctl -b -u phoniebox-bt-buttons.service
#   Check with >bluetoothctl info, if the headset is connected, play some music to be sure. Check /dev/input/eventX exists and check >cat /proc/bus/input/devices
#   Then go back to starting the script in the console and take a look at the messages (stop the service first)

BTNPLAY  = 200
BTNPAUSE = 201
BTNNEXT  = 163
BTNPREV  = 165

EVTDEV='/dev/input/event0'

def btkeyhandler():
    # Try to open the event device
    dev = InputDevice(EVTDEV)
    print(dev)
    # Infinite loop reading the events. Will fail, if event device gets disconnected
    for event in dev.read_loop():
        if event.type == ecodes.EV_KEY:
            # Report the button event
            print(categorize(event))
            # Only act on button press, not button release
            if event.value == 1:
                if event.code == BTNPLAY:
                    check_call("../../scripts/playout_controls.sh -c=playerpause", shell=True)
                elif event.code == BTNPAUSE:
                    check_call("../../scripts/playout_controls.sh -c=playerpause", shell=True)
                elif event.code == BTNNEXT:
                    check_call("../../scripts/playout_controls.sh -c=playernext", shell=True)
                elif event.code == BTNPREV:
                    check_call("../../scripts/playout_controls.sh -c=playerprev", shell=True)
        
while True:
    try:
        btkeyhandler()
        break
    except FileNotFoundError:
        # Sleeping in long intervalls when headset is not connected
        time.sleep(3)
            
