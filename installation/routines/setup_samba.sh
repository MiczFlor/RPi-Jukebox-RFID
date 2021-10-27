#!/usr/bin/env bash

_samba_install_os_dependencies() {
  echo "Install Samba Core dependencies"
  sudo apt-get -qq -y update; sudo apt-get -qq -y install \
    samba samba-common-bin \
    --no-install-recommends \
    --allow-downgrades \
    --allow-remove-essential \
    --allow-change-held-packages
}

_samba_set_user() {
  local SMB_CONF="/etc/samba/smb.conf"
  local SMB_USER="pi"
  local SMB_PASSWD="raspberry"

  # Samba has not been configured
  if grep -q "## Jukebox Samba Config" "$SMB_CONF"; then
    echo "  Skipping. Already set up!" | tee /dev/fd/3
  else
    # Create Samba user
    (echo "${SMB_PASSWD}"; echo "${SMB_PASSWD}") | sudo smbpasswd -s -a $SMB_USER

    sudo chown root:root $SMB_CONF
    sudo chmod 777 $SMB_CONF

    # Create Samba Mount Points
    sudo cat << EOF >> $SMB_CONF
## Jukebox Samba Config
[phoniebox]
  comment= Pi Jukebox
  path=${SHARED_PATH}
  browseable=Yes
  writeable=Yes
  only guest=no
  create mask=0777
  directory mask=0777
  public=no
EOF

    sudo chmod 644 $SMB_CONF
  fi
}

setup_samba() {
  echo "Install Samba and configure user" | tee /dev/fd/3

  # Skip interactive Samba WINS config dialog
  echo "samba-common samba-common/dhcp boolean false" | sudo debconf-set-selections
  _samba_install_os_dependencies
  _samba_set_user

  echo "DONE: setup_samba"
}
