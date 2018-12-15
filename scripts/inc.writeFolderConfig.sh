#!/bin/bash

# This script is important.
# This script manages the creation and changing of folder.conf
# folder.conf sits in the audio folder and will grow over time,
# containing all infos about how to play the content
# such as loop, resume play, shuffle, elapsed time, etc.
# 
# The functionality seems weird (but makes total sense:). 
# This is how it works:
# 1. Since this file will be called from another bash, we can assume that
#    we have same variables that need saving: check each and make a copy
#    under a different name.
# 2. Read the current folder config file - now we have the vars in memory.
# 3. Create a raw config file instead of the current folder config
#    which allows to replace new vars and keep the old
# 4. For each var in the config file:
#    IF new var available, write this one
#    ELSE write the one we read in step 2.
#
# Why so complicated? Because we don't know what other vars will be in the 
# folder config in the future. Editing only the sample config file and this
# file, we are future proof, because old config files will work and update
# gracefully when new stuff arrives in the sample file.

# We start from a sample file that contains vars like these:
# CURRENTFILENAME="%CURRENTFILENAME%"
# ELAPSED="%ELAPSED%"
# ...
#
# For complete control, the creatin of this raw config sample 
# is also kept in this script and write if from here.
# So that all new vars etc. only require changing this file.

#############################################################
# VARIABLES

# $DEBUG true|false
DEBUG=false

# Set the date and time of now
NOW=`date +%Y-%m-%d.%H:%M:%S`

# path of this file
PATHDATA="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Get args from command line. Needed for "create default folder.conf" file
# see following file for details:
. $PATHDATA/inc.readArgsFromCommandLine.sh

# IMPORTANT: the $FOLDER var does not need to be passed on if it was set in the master script
# that calls this one. For elegance, it might be better to pass it on.
# And for error checking this might mean: if $FOLDER is not passed on, exit, do not do anything.
# If this would be preferred by you, the users, please file a ticket to discuss it.

# path to audio folders
AUDIOFOLDERSPATH=`cat $PATHDATA/../settings/Audio_Folders_Path`

# some debug info
if [ "$DEBUG" == "true" ]; then echo "########### SCRIPT inc.writeFolderConfig.sh ($NOW) ##" >> $PATHDATA/../logs/debug.log; fi
if [ "$DEBUG" == "true" ]; then echo "VAR COMMAND: $COMMAND" >> $PATHDATA/../logs/debug.log; fi
if [ "$DEBUG" == "true" ]; then echo "VAR FOLDER: $FOLDER" >> $PATHDATA/../logs/debug.log; fi
if [ "$DEBUG" == "true" ]; then echo "VAR AUDIOFOLDERSPATH: $AUDIOFOLDERSPATH" >> $PATHDATA/../logs/debug.log; fi


if [ "$DEBUG" == "true" ]; then echo "CHECK FOLDER EXISTS: ${AUDIOFOLDERSPATH}/${FOLDER}" >> $PATHDATA/../logs/debug.log; fi
# Only continue if $FOLDER exists
if [ -d "${AUDIOFOLDERSPATH}/${FOLDER}" ]
then

    # IF we got given the command to create a default folder.conf file
    # set default vars, write file, exit
    if [ $COMMAND == "createDefaultFolderConf" ]
    then
        if [ "$DEBUG" == "true" ]; then echo "  !!!setting default vars for raw create!!!" >> $PATHDATA/../logs/debug.log; fi
        # set default vars
        CURRENTFILENAME="filename"
        ELAPSED="0"
        PLAYSTATUS="Stopped"
        RESUME="OFF"
        SHUFFLE="OFF"
        LOOP="OFF"
    fi
    
    #########################################################
    # KEEP NEW VARS IN MIND
    # Go through all given vars - make copy with prefix if found
    if [ "$DEBUG" == "true" ]; then echo "  KEEP NEW VARS IN MIND" >> $PATHDATA/../logs/debug.log; fi
    if [ "$CURRENTFILENAME" ]; then 
        NEWCURRENTFILENAME="$CURRENTFILENAME"; 
        if [ "$DEBUG" == "true" ]; then echo "VAR NEWCURRENTFILENAME: $NEWCURRENTFILENAME" >> $PATHDATA/../logs/debug.log; fi
    fi
    if [ "$ELAPSED" ]; then NEWELAPSED="$ELAPSED"; fi
    if [ "$PLAYSTATUS" ]; then NEWPLAYSTATUS="$PLAYSTATUS"; fi
    if [ "$RESUME" ]; then NEWRESUME="$RESUME"; fi
    if [ "$SHUFFLE" ]; then NEWSHUFFLE="$SHUFFLE"; fi
    if [ "$LOOP" ]; then NEWLOOP="$LOOP"; fi

    # Read the current config file (include will execute == read)
    . "${AUDIOFOLDERSPATH}/${FOLDER}/folder.conf"
    if [ "$DEBUG" == "true" ]; then echo "  content of ${AUDIOFOLDERSPATH}/${FOLDER}/folder.conf" >> $PATHDATA/../logs/debug.log; fi
    if [ "$DEBUG" == "true" ]; then cat "${AUDIOFOLDERSPATH}/${FOLDER}/folder.conf" >> $PATHDATA/../logs/debug.log; fi

    #########################################################
    # RAW CONFIG FILE
    # Replace current config with empty sample    
    # write "empty" config file with vars that will be replaced later
    rm "${AUDIOFOLDERSPATH}/${FOLDER}/folder.conf"
    echo "CURRENTFILENAME=\"%CURRENTFILENAME%\"" >> "${AUDIOFOLDERSPATH}/${FOLDER}/folder.conf"
    echo "ELAPSED=\"%ELAPSED%\"" >> "${AUDIOFOLDERSPATH}/${FOLDER}/folder.conf"
    echo "PLAYSTATUS=\"%PLAYSTATUS%\"" >> "${AUDIOFOLDERSPATH}/${FOLDER}/folder.conf"
    echo "RESUME=\"%RESUME%\"" >> "${AUDIOFOLDERSPATH}/${FOLDER}/folder.conf"
    echo "SHUFFLE=\"%SHUFFLE%\"" >> "${AUDIOFOLDERSPATH}/${FOLDER}/folder.conf"
    echo "LOOP=\"%LOOP%\"" >> "${AUDIOFOLDERSPATH}/${FOLDER}/folder.conf"

    # Let the juggle begin
    
    #########################################################
    # REPLACE VALUES FROM THE CONFIG FILE WITH NEW ONES
    # Walk through all vars and prefer new over existing to write to config
    if [ "$DEBUG" == "true" ]; then echo "  REPLACE VALUES FROM THE CONFIG FILE WITH NEW ONES" >> $PATHDATA/../logs/debug.log; fi
    if [ "$NEWCURRENTFILENAME" ]; then 
        CURRENTFILENAME="$NEWCURRENTFILENAME"; 
        if [ "$DEBUG" == "true" ]; then echo "VAR CURRENTFILENAME: $CURRENTFILENAME" >> $PATHDATA/../logs/debug.log; fi
    fi
    if [ "$NEWELAPSED" ]; then ELAPSED="$NEWELAPSED"; fi
    if [ "$NEWPLAYSTATUS" ]; then PLAYSTATUS="$NEWPLAYSTATUS"; fi
    if [ "$NEWRESUME" ]; then RESUME="$NEWRESUME"; fi
    if [ "$NEWSHUFFLE" ]; then SHUFFLE="$NEWSHUFFLE"; fi
    if [ "$NEWLOOP" ]; then LOOP="$NEWLOOP"; fi
    
    #########################################################
    # WRITE THE VALUES INTO THE NEWLY CREATED RAW CONFIG
    # for $CURRENTFILENAME using | as alternate regex delimiter because of the folder path slash 
    if [ "$DEBUG" == "true" ]; then echo "  WRITE THE VALUES INTO THE NEWLY CREATED RAW CONFIG" >> $PATHDATA/../logs/debug.log; fi
    sudo sed -i 's|%CURRENTFILENAME%|'"$CURRENTFILENAME"'|' "${AUDIOFOLDERSPATH}/${FOLDER}/folder.conf"
    sudo sed -i 's/%ELAPSED%/'"$ELAPSED"'/' "${AUDIOFOLDERSPATH}/${FOLDER}/folder.conf"
    sudo sed -i 's/%PLAYSTATUS%/'"$PLAYSTATUS"'/' "${AUDIOFOLDERSPATH}/${FOLDER}/folder.conf"
    sudo sed -i 's/%RESUME%/'"$RESUME"'/' "${AUDIOFOLDERSPATH}/${FOLDER}/folder.conf"
    sudo sed -i 's/%SHUFFLE%/'"$SHUFFLE"'/' "${AUDIOFOLDERSPATH}/${FOLDER}/folder.conf"
    sudo sed -i 's/%LOOP%/'"$LOOP"'/' "${AUDIOFOLDERSPATH}/${FOLDER}/folder.conf"
    sudo chown pi:www-data "${AUDIOFOLDERSPATH}/${FOLDER}/folder.conf"
    sudo chmod 777 "${AUDIOFOLDERSPATH}/${FOLDER}/folder.conf"

else
    if [ "$DEBUG" == "true" ]; then echo "NOT FOUND: Full path to folder '${AUDIOFOLDERSPATH}/${FOLDER}'" >> $PATHDATA/../logs/debug.log; fi
fi




