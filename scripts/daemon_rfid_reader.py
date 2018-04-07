import subprocess
import os , signal
import time
import sys
import logging
from Reader import Reader


# setup Basic logging to file
logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', datefmt='%I:%M:%S', level=logging.DEBUG, filename='./daemon_rfid.log', filemode='w') # change filemode to 'a' for an continues logfile
# Logging for console
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
console_format = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
console.setFormatter(console_format)
# add the handler to the root logger
logging.getLogger('').addHandler(console)



# Handler if the process is killed (by OS during shutdown most probably)
def sigterm_handler(signal, frame):
    check_kill_process("vlc")
    logging.info("Exit Daemon RFID")
    logging.shutdown()
    # Exit Task
    sys.exit(0)
# end def sigterm_handler



# function to kill a VLC processes
def check_kill_process(pstring):
    for line in os.popen("ps ax | grep " + pstring + " | grep -v grep"):
        fields = line.split()
        pid = fields[0]
        logging.info("Killing VLC PID: %s" % pid)
        os.kill(int(pid), signal.SIGKILL)
#end def check_kill_process
        


# register SIGTERM and SIGINT handler
signal.signal(signal.SIGTERM, sigterm_handler)
signal.signal(signal.SIGINT, sigterm_handler)

# Setup reader object
reader = Reader()

# Check if devie found
if reader.dev != None:

	# get absolute path of this script
	dir_path = os.path.dirname(os.path.realpath(__file__))
			
	# Lets start the daemon and wait for RFID
	while True:
		# reading the card id - blocking call
		cardid = reader.readCard()
		# cardid = input("ID: ")

		logging.info("Card ID %s was used.", cardid )
		# TODO log to file -  > $PATHDATA/../shared/latestID.txt

		music_folder  = os.path.join(dir_path, '../shared/audiofolders', str(cardid) )
		playlist_file = os.path.join(dir_path, '../playlists', str(cardid) + '.m3u' )

		# Expected folder structure:
		#
		# $dir_path + /../shared/audiofolders/ + cardid
		# $dir_path + /../shared/playlists/ + cardid + ".m3u"

		# if a music_folder , change playlist- else just print warning
		
		if (os.path.exists( music_folder ) ):
			# create playlist in the folder 
			musicfiles = [f for f in os.listdir(music_folder) if os.path.isfile(os.path.join(music_folder, f))]
			
			logging.info("Check %s for music.", music_folder )
			# check if files are there
			if (musicfiles != []):
				# create new play list
				playlist = open(playlist_file, 'w')
				
				for file in musicfiles:
					playlist.write(os.path.join('../shared/audiofolders', str(cardid), '%s\n' % (file)))
				playlist.close()
				
				# kill all process with vlc in it
				check_kill_process("vlc")
				
				# assemble command
				command = "cvlc -I rc --rc-host localhost:4212 %s" % (playlist_file)
				
				logging.info("Command: %s", command )
				# set VLC to new playlist
				pid = subprocess.Popen(command,  shell=True,stdin=None, stdout=None, stderr=None, close_fds=True)
				logging.info("Started process: %d", pid.pid )
			else:
				#
				logging.warning("No files in %s.", music_folder )
			#endif 
			
		else:
			# folder does not exists
			logging.warning("No Folder for Card ID %s : %s", cardid, music_folder )
		#endif

	#end while
else:
	if reader.deviceName :
		logging.error('Could not find the device %s\n. Make sure is connected' % deviceName)		
	else:
		# file is created by using script RegisterDevice.py
		logging.error("No Device configured. Execute RegisterDevice.py")
