#!/usr/bin/env bash

set_ssh_qos() {
    if [ "$DISABLE_SSH_QOS" == true ] ; then
        # The latest version of SSH installed on the Raspberry Pi 3 uses QoS headers, which disagrees with some
        # routers and other hardware. This causes immense delays when remotely accessing the RPi over ssh.
        log "  Set SSH QoS to best effort"
        echo -e "IPQoS 0x00 0x00\n" | sudo tee -a /etc/ssh/sshd_config
        echo -e "IPQoS 0x00 0x00\n" | sudo tee -a /etc/ssh/ssh_config
    fi
}
