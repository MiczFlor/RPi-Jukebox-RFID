#!/usr/bin/python
# Currently only work in python 2.7 - .send works with str here

# Related to page: https://forum-raspberrypi.de/forum/thread/13144-projekt-jukebox4kids-jukebox-fuer-kinder/?postID=312257#post312257

# Depends on libs:
# nclib    - https://nclib.readthedocs.io/en/latest/  - pip install nclib
# gpiozero -
# KY040    - git link to my repo 

from gpiozero import Button
from gpiozero import LED
from subprocess import check_call
import signal
import time
import sys
import logging
import nclib
import errno
from socket import error as socket_error

# Added as submodle in GIT
from KY040 import KY040


# setup Basic logging to file
logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', datefmt='%I:%M:%S', level=logging.DEBUG, filename='./buttons.log', filemode='w')
# Logging for console
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
console_format = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
console.setFormatter(console_format)
# add the handler to the root logger
logging.getLogger('').addHandler(console)

# Shutdown Counter in seconds - Default time
DEFAULT_SHUTDOWN_TIME_S = 5 * 60

def nc_send(command):
    global nc
    try:
		if nc != None:
			# do something
			nc.send(command + '\n')
		else:
			logging.info('Command %s not executed, as VLC connection not established.' %(command))
    except socket_error as e:
        # A socket error
        print (e)
        # import pdb; pdb.set_trace()
        # delete nc
        nc = None



# Handler if the process is killed (by OS during shutdown most probably)
def sigterm_handler(signal, frame):
    logging.info("Jukebox Stopped")
    # Stop the player
    if nc != None:
        nc_send('stop')
        nc.close()  
    logging.info("VLC Stop Play")
    logging.info("Switch Off Relais")
    # Switch of relais
    led.off()
    # Wait 1 seconds
    time.sleep(1)
    logging.info("Exit Task")
    logging.shutdown()
    # Exit Task
    sys.exit(0)
# end def sigterm_handler

def def_shutdown():
    logging.info("Switch Off Relais")
    # Switch of relais
    led.off()
    nc_send('stop')
    nc.close()  
    # Wait 1 seconds
    time.sleep(1)
    logging.info("Calling PowerOff")
    logging.shutdown()
    check_call(['sudo', 'poweroff'])

def def_vol(direction):
    if (direction == KY040.CLOCKWISE):
        check_call("amixer sset PCM 1.5db+", shell=True)
        logging.info("Volume Increase")
    else:
        check_call("amixer sset PCM 1.5db-", shell=True)
        logging.info("Volume Decrease")
#end def

def def_vol0():
    check_call("amixer sset PCM toggle", shell=True)
    logging.info("Mute/Unmute")

def def_next():
    nc_send('next')
    logging.info("Next Titel")

def def_prev():
    nc_send('prev')
    logging.info("Prev Titel")

def def_pause():
    global playing, play_pause
    nc_send('pause')
    logging.info("Pause Play")
    # button pressed - set timeout-value
    shutdown_timer = DEFAULT_SHUTDOWN_TIME_S
    playing = False
    # toggle to play handler
    play_pause.when_pressed = def_play
#end def_pause

def def_play():
    global playing, play_pause
    nc_send('play')
    logging.info("Start Playing")
    # button pressed
    playing = True
    shutdown_timer = DEFAULT_SHUTDOWN_TIME_S 
    # toggle to pause handler
    play_pause.when_pressed = def_pause
#end def_play

led = LED(15)
shut = Button(3, hold_time=2)
next = Button(17, bounce_time=0.050)
prev = Button(27, bounce_time=0.050)
play_pause = Button(26)

# register SIGTERM handler
signal.signal(signal.SIGTERM, sigterm_handler)
signal.signal(signal.SIGINT, sigterm_handler)

shut.when_held    = def_shutdown
next.when_pressed = def_next
prev.when_pressed = def_prev
play_pause.when_pressed = def_play

# Create a KY040 and start it
ky040 = KY040(23, 22, 21, def_vol, def_vol0)
ky040.start()

# Shutdown tracking globals
playing = False # default startup, nothing is playing
shutdown_timer = DEFAULT_SHUTDOWN_TIME_S

# Switch on Relais
led.on()

nc = None
# Shutdown countdown
while (shutdown_timer > 0) :
    
    if nc == None:
        # start a new Netcat() instance
        try:
            logging.info("Connecting to VLC")
            nc = nclib.Netcat(('localhost', 4212))
        except nclib.errors.NetcatError:
            logging.error("VLC seems to be down - try to reconnect in 1 second")
            nc = None
    if (playing == False):
        logging.info("Seconds Remaining: %s" % shutdown_timer)
        # countdown - not playing
        shutdown_timer = shutdown_timer - 1
    elif (playing == True):
        shutdown_timer = DEFAULT_SHUTDOWN_TIME_S 
    #end if
    # sleep 1 second
    time.sleep(1)
#end while
# Timeout reached, shutdown system
def_shutdown()

