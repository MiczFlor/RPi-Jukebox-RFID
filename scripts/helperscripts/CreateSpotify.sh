#!/bin/bash

# this script adds a Spotify album or element to you library
#
# agruments of this script:
# folder is the root folder in the player
# item is the name of the Spotify element and will be used for the subfolder
# Spotify is the ID of the element in Spotify, 
#  you can get it in the spotifiy player, when you copy the URI

POSITIONAL=()
while [[ $# -gt 0 ]]
do
key="$1"

case $key in
    -f|--folder)
    FOLDERNAME="$2"
    shift # past argument
    shift # past value
    ;;
    -i|--item)
    ITEMNAME="$2"
    TITLE="$2"
    shift # past argument
    shift # past value
    ;;
    -s|--spotify)
    SPOTIFYID="$2"
    shift # past argument
    shift # past value
    ;;
    --default)
    DEFAULT=YES
    shift # past argument
    ;;
    *)    # unknown option
    POSITIONAL+=("$1") # save it in an array for later
    shift # past argument
    ;;
esac
done

if [[ -z $FOLDERNAME ]]; then
    echo "please give argument --folder or -f"
    echo "${0} -f <FOLDER> -i <ITEMNAME> -s <SPOTIFYID>"
    exit 1
fi

if [[ -z $ITEMNAME ]]; then
    echo "please give argument --item or -i"
    echo "${0}-f <FOLDER> -i <ITEMNAME> -s <SPOTIFYID>"
    exit 1
fi

if [[ -z $SPOTIFYID ]]; then
    echo "please give argument --spotify or -s e.g.: spotify:ablum:0Xr3uVyTkcDiCKzDWGA5ik"
    echo "${0} -f <FOLDER> -i <ITEMNAME> -s <SPOTIFYID>"
    exit 1
fi

#echo "FOLDERNAME    = ${FOLDERNAME}"
#echo "ITEMNAME      = ${ITEMNAME}"
#echo "SPOTIFYID     = ${SPOTIFYID}"

# Creates sample folders with files and streams 
# inside the $AUDIOFOLDERSPATH directory

PATHDATA="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# move to this directory to make sure relative paths work
cd $PATHDATA

AUDIOFOLDERSPATH=`cat ../../settings/Audio_Folders_Path`

mkdir $AUDIOFOLDERSPATH/$FOLDERNAME/ -p
mkdir $AUDIOFOLDERSPATH/$FOLDERNAME/$ITEMNAME -p

echo CURRENTFILENAME="filename"\n\
ELAPSED="0"\n\
PLAYSTATUS="Stopped"\n\
RESUME="OFF"\n\
SHUFFLE="OFF"\n\
LOOP="OFF"\n\
SINGLE="OFF"\n\
> $AUDIOFOLDERSPATH/$FOLDERNAME/$ITEMNAME/folder.conf
echo $SPOTIFYID > $AUDIOFOLDERSPATH/$FOLDERNAME/$ITEMNAME/spotify.txt
echo $TITLE > $AUDIOFOLDERSPATH/$FOLDERNAME/$ITEMNAME/title.txt



# chmod chown
sudo chown -R :www-data $AUDIOFOLDERSPATH/$FOLDERNAME*
sudo chmod -R 777 $AUDIOFOLDERSPATH/$FOLDERNAME*
