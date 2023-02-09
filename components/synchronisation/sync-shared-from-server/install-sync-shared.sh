#!/bin/bash

PATHDATA="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJROOTPATH="${PATHDATA}/../../.."

# Ensure script is executable for everyone
sudo chmod ugo+rx "${PATHDATA}/sync-shared.sh"

# Make sure required packages are installed
echo -e "\nChecking rsync packages"
sudo apt install rsync -y

if [ ! -f ${PROJROOTPATH}/settings/sync_shared.conf ]; then
    cp ${PATHDATA}/settings/sync_shared.conf.sample ${PROJROOTPATH}/settings/sync_shared.conf
    # change the read/write so that later this might also be editable through the web app
    sudo chown -R pi:www-data ${PROJROOTPATH}/settings/sync_shared.conf
    sudo chmod -R ugo+rw ${PROJROOTPATH}/settings/sync_shared.conf
fi

# Let global controls know this feature is enabled
echo -e "\nLet global controls know this feature is enabled (Sync_Shared_Enabled -> TRUE)"
CONFFILE="${PROJROOTPATH}/settings/Sync_Shared_Enabled"
echo "TRUE" > ${CONFFILE}
chmod ugo+rw ${CONFFILE}

# Final notes
echo -e "\n\n\nFINAL NOTE:\nPlease check README.md for further configuration"