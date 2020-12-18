#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec  8 17:39:01 2020

Provides btSwitch (see below) as function and callable script

If called as script, configure led_pin according to your set-up

@author: chris
"""

import sys
import re
import subprocess

# If called as script, this variable will set GPIO number of the LED to reflect sink status
# Uses BCM GPIO numbering, i.e. 'led_pin = 6' means GPIO6
# Set 'led_pin=None' to disable LED support (and no GPIO pin is blocked in this case)
led_pin = None

def btUsage(sname):
    print("Usage")
    print("  ./" + sname + "[ toggle | speakers | headphones]")
   
def btSwitch(cmd, led_pin=None):
    """
    Set/Toggle between regular speakers and headphone output. If no bluetooth device is connected, always defaults to mpc output 1
        
    To be precise: toggle between mpc output 1 and mpc output 2.
    
    So, set up your /etc/mpd.conf correctly: first audio_output section should be speakers, second audio_output section should be headphones
    To set up bluetooth headphones, follow the wiki
    Short guide to connect bluetooth (without audio setup)
        sudo bluetoothctl
        power on
        agent on
        scan on                   -> shows list of Bluetooth devices in reach
        pair C4:FB:20:63:A7:F2    -> pairing happens
        trust C4:FB:20:63:A7:F2   -> trust you device
        connect C4:FB:20:63:A7:F2 -> connect
        scan off
        exit
    Next time headphones are switched on, they should connect automatically
    
    Requires
      sudo apt install bluetooth
    
    Attention
      The user to runs this script (precisly who runs bluetoothctl) needs proper access rights. Otherwise bluetoothctl will always return "no default controller found"
      The superuser and users of group "bluetooth" have these. You can check the policy here
        /etc/dbus-1/system.d/bluetooth.conf
      Best to check first if the user which later runs this script can execute bluetoothctl and get meaningful results 
        sudo -u www-data bluetoothctl show
        E.g. if you want to do bluetooth manipulation from the web interface, you will most likely need to add www-data to the group bluetooth
             if you want to test this script from the command line, you will most likely need to add user pi (or whoever you are) to the group bluetooth or run it as superuser
        sudo usermod -G bluetooth -a www-data
      Don't forget to reboot for group changes to take effect here
  
    LED support
      If LED number (GPIO number, BCM) is provided, a LED is switched to reflect output sink status
      off = speakers, on = headphones
      LED blinks if no bluetooth device is connected and bluetooth sink is requested, before script default to output 1
      
      A note for developers: This script is not persistent and only gets called (from various sources) when the output sink is changed/toggled and exits. 
        This is done to make is callable from button press (gpio button handler), rfid card number, web interface
        The LED state however should be persistent. With GPIOZero, the LED state gets reset at the end of the script. For that reason GPIO state is manipulated through shell commands
  
    Parameters
    ----------
    cmd : string
        toggle | speakers | headphones
        
    led_pin : integer
        GPIO pin number of LED to reflect output status. If None, LED support is disabled (and no GPIO pin is blocked)
   """
    # Check for valid command
    if cmd != "toggle" and cmd != "speakers" and cmd != "headphones":
        print("Error: Invalid command. Doing nothing.")
        return
    
    # Rudimentary check if LED pin request is valid GPIO pin number
    if led_pin is not None:
        if led_pin < 2 or led_pin > 27:
            led_pin = None
            print("- ERROR: Invalid led_pin. Ignoring led_pin = " + str(led_pin), file=sys.stderr)
    
    if led_pin is not None:
        # Set-up GPIO LED pin if not already configured. If it already exists, sanity check direction of pin before use
        try:
            with open("/sys/class/gpio/gpio" + str(led_pin) + "/direction") as f:
                if f.readline(3) != "out":
                    print("- ERROR: LED pin already in use with direction 'in'. Ignoring led_pin = " + str(led_pin), file=sys.stderr)
                    led_pin = None
        except:
            # GPIO direction file does not exist -> pin is not configured. Set it up (sleep is necessary!)
            subprocess.run("echo " + str(led_pin) + " > /sys/class/gpio/export; \
                           sleep 0.1; \
                           echo out > /sys/class/gpio/gpio" + str(led_pin) + "/direction", shell=True, check=False)
        
    # Figure out if output 1 (speakers) is enabled
    isSpeakerOn_console = subprocess.run("mpc outputs", shell=True, check=False, capture_output=True)
    isSpeakerOn = re.search(b"1.*enabled", isSpeakerOn_console.stdout)

    # Figure out if a bluetooth device is connected (any device will do). Assume here that only speakers/headsets will be connected
    # -> No need for user to adapt MAC address
    # -> will actually support multiple speakers/headsets paired to the phoniebox
    # Alternative: Check for specific bluetooth device only with "bluetoothctl info MACADDRESS"
    isBtConnected_console = subprocess.run("bluetoothctl info", shell=True, check=False, capture_output=True)
    isBtConnected = re.search(b"Connected:\s+yes", isBtConnected_console.stdout)        
                      
    if ((cmd == "toggle" and isSpeakerOn) or (cmd == "headphones")):
        # Only switch to BT headphones if they are actually connected
        if isBtConnected:
            print("Switched audio sink to \"Output 2\"")
            subprocess.run("mpc enable only 2", shell=True, check=False, capture_output=True);
            if led_pin is not None:
                subprocess.run("echo 1 > /sys/class/gpio/gpio" + str(led_pin) + "/value", shell=True, check=False)
            return
        else: 
            print("No bluetooth device connected. Defaulting to \"Output 1\".")
            if led_pin:
                sleeptime = 0.25
                for i in range(0,3):
                    subprocess.run("echo 1 > /sys/class/gpio/gpio" + str(led_pin) + "/value; sleep " + str(sleeptime) + "; echo 0 > /sys/class/gpio/gpio" + str(led_pin) + "/value; sleep " + str(sleeptime), shell=True, check=False)

    # Default: Switch to Speakers
    print("Switched audio sink to \"Output 1\"")
    subprocess.run("mpc enable only 1", shell=True, check=False, capture_output=True);
    if led_pin:
        subprocess.run("echo 0 > /sys/class/gpio/gpio" + str(led_pin) + "/value", shell=True, check=False)


if __name__ == "__main__":
        if len(sys.argv) == 2:            
            btSwitch(sys.argv[1], led_pin)
        else:
            btUsage(sys.argv[0])
            
