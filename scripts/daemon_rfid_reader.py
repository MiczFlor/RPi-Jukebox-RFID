import subprocess
import os 
from Reader import Reader

reader = Reader()

# get absolute path of this script
dir_path = os.path.dirname(os.path.realpath(__file__))

print dir_path


base_path = os.path.dirname(dir_path)

try:
   # clear last played folder and playlist to avoid that last card wasn't able to play after system reboot
   subprocess.call(['echo "" >' + base_path + '/settings/Latest_Folder_Played'], shell=True)
   subprocess.call(['echo "" >' + base_path + '/settings/Latest_Playlist_Played'], shell=True)
except OSError as e:
   print "Execution failed:"



while True:
        # reading the card id
        cardid = reader.readCard()
        try:
            # start the player script and pass on the cardid 
            subprocess.call([dir_path + '/rfid_trigger_play.sh --cardid=' + cardid], shell=True)
        except OSError as e:
            print "Execution failed:" 
