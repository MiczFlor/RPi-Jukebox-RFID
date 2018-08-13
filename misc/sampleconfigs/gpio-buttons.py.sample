#!/usr/bin/python3
from gpiozero import Button
from signal import pause
from subprocess import check_call

# 2017-12-12
# This script was copied from the following RPi forum post:
# https://forum-raspberrypi.de/forum/thread/13144-projekt-jukebox4kids-jukebox-fuer-kinder/?postID=312257#post312257
# I have not yet had the time to test is, so I placed it in the misc folder.
# If anybody has ideas or tests or experience regarding this solution, please create pull requests or contact me.

def def_shutdown():
    check_call("./scripts/playout_controls.sh -c=shutdown", shell=True)

def def_volU():
    check_call("./scripts/playout_controls.sh -c=volumeup", shell=True)

def def_volD():
    check_call("./scripts/playout_controls.sh -c=volumedown", shell=True)

def def_vol0():
    check_call("./scripts/playout_controls.sh -c=mute", shell=True)

def def_next():
    check_call("./scripts/playout_controls.sh -c=playernext", shell=True)

def def_prev():
    check_call("./scripts/playout_controls.sh -c=playerprev", shell=True)

def def_halt():
    check_call("./scripts/playout_controls.sh -c=playerpause", shell=True)

shut = Button(3, hold_time=2)
vol0 = Button(13)    
volU = Button(16,pull_up=True)
volD = Button(19,pull_up=True)
next = Button(26)
prev = Button(20)
halt = Button(21)

shut.when_held = def_shutdown
vol0.when_pressed = def_vol0
volU.when_pressed = def_volU
volD.when_pressed = def_volD
next.when_pressed = def_next
prev.when_pressed = def_prev
halt.when_pressed = def_halt

pause()
