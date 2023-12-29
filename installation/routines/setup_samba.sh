#!/usr/bin/env bash

SMB_CONF="/etc/samba/smb.conf"
SMB_CONF_HEADER="## Jukebox Samba Config"

_samba_install_os_dependencies() {
  log "  Install Samba Core dependencies"
  sudo apt-get -qq -y update; sudo apt-get -qq -y install \
    samba samba-common-bin \
    --no-install-recommends \
    --allow-downgrades \
    --allow-remove-essential \
    --allow-change-held-packages
}

_samba_set_user() {
  print_lc "  Configure Samba"
  local SMB_PASSWD="raspberry"

  # Samba has not been configured
  if grep -q "$SMB_CONF_HEADER" "$SMB_CONF"; then
    print_lc "    Skipping. Already set up!"
  else
    # Create Samba user
    (echo "${SMB_PASSWD}"; echo "${SMB_PASSWD}") | sudo smbpasswd -s -a "${CURRENT_USER}"

    sudo chown root:root $SMB_CONF
    sudo chmod 777 $SMB_CONF

    # Create Samba Mount Points
    sudo cat << EOF >> $SMB_CONF
${SMB_CONF_HEADER}
[phoniebox]
  comment=Pi Jukebox
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

_samba_check() {
    print_verify_installation

    verify_apt_packages samba samba-common-bin

    verify_files_chmod_chown 644 root root "${SMB_CONF}"

    verify_file_contains_string "${SMB_CONF_HEADER}" "${SMB_CONF}"
    verify_file_contains_string "${SHARED_PATH}" "${SMB_CONF}"

    if ! (sudo pdbedit -L | grep -qw "^${CURRENT_USER}") ; then
        exit_on_error "ERROR: samba user not found"
    fi
}

_run_setup_samba() {
    # Skip interactive Samba WINS config dialog
    echo "samba-common samba-common/dhcp boolean false" | sudo debconf-set-selections
    _samba_install_os_dependencies
    _samba_set_user
    _samba_check
}

setup_samba() {
    if [ "$ENABLE_SAMBA" == true ] ; then
        run_with_log_frame _run_setup_samba "Install Samba"
    fi
}
