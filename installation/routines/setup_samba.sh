#!/usr/bin/env bash

SMB_CONF="/etc/samba/smb.conf"
SMB_CONF_HEADER="## Jukebox Samba Config"

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
  local SMB_USER="pi"
  local SMB_PASSWD="raspberry"

  # Samba has not been configured
  if grep -q "$SMB_CONF_HEADER" "$SMB_CONF"; then
    echo "  Skipping. Already set up!" | tee /dev/fd/3
  else
    # Create Samba user
    (echo "${SMB_PASSWD}"; echo "${SMB_PASSWD}") | sudo smbpasswd -s -a $SMB_USER

    sudo chown root:root $SMB_CONF
    sudo chmod 777 $SMB_CONF

    # Create Samba Mount Points
    sudo cat << EOF >> $SMB_CONF
${SMB_CONF_HEADER}
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

_samba_check () {
    echo "Check Samba Installation" | tee /dev/fd/3
    verify_apt_packages samba samba-common-bin

    verify_files_chmod_chown 644 root root "${SMB_CONF}"

    verify_file_contains_string "${SMB_CONF_HEADER}" "${SMB_CONF}"
    verify_file_contains_string "${SHARED_PATH}" "${SMB_CONF}"
}

setup_samba() {
    if [ "$ENABLE_SAMBA" == true ] ; then
        echo "Install Samba and configure user" | tee /dev/fd/3

        # Skip interactive Samba WINS config dialog
        echo "samba-common samba-common/dhcp boolean false" | sudo debconf-set-selections
        _samba_install_os_dependencies
        _samba_set_user
        _samba_check

        echo "DONE: setup_samba"
    fi
}
