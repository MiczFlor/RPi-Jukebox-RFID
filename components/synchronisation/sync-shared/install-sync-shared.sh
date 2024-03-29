#!/bin/bash

# Ensure start was intended
read -rp "Start installation? [Y/n] " response
case "$response" in
    [nN][oO]|[nN])
        echo "Installation aborted..."
        exit
        ;;
    *)
        ;;
esac

PATHDATA="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJROOTPATH="${PATHDATA}/../../.."

# Ensure script is executable for everyone
sudo chmod ugo+rx "${PATHDATA}/sync-shared.sh"

# Make sure required packages are installed
echo -e "\nChecking rsync package"
sudo apt install rsync -y
echo -e "\nChecking ssh package"
sudo apt install openssh-client -y

"${PATHDATA}"/change-configuration.sh "SkipInitialCheck"

echo -e "\n\nFINAL NOTE:\nPlease check README.md for further configuration"
