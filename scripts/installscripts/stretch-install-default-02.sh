# sketch for a luxury one line install script
# DO NOT USE UNTIL THIS LINE HAS DISAPPEARED
Ask if wifi config
Ask if Spotify config
Ask if access point

If wifi
Ask for ssid
Ask for password
Ask for IP

If Spotify
Ask for user
Ask for password

Ask samba password
Ask ssh password

# check for existkng Phoniebox installation
# change to home directory to check relative paths
cd
# phoniebox dir exists?
# shortcuts dir exists and not empty?
# audiofolders exists and not empty?
# card ID conf exists?
# GPIO file exists?
# Sounds startup Shutdown?
Echo install found
Ask if existing files and ocnfig should be used? All/None/Specify individually

# NONE delete Phoniebox dir
# ELSE 
## del dir BACKUP
## move Phoniebox dir to BACKUP

# get existing install
# new config should be done with sed using existing conf and user input
# samba nad yss password iwthout prompt

# CLEANUP
## remove dir BACKUP (possibly not, because we od this ta the ebginning after user confirms for latest config)
