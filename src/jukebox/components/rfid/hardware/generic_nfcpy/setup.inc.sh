#!/usr/bin/env bash

CURRENT_USER="${SUDO_USER:-$(whoami)}"

modprobe_file="/etc/modprobe.d/disable_driver_jukebox_nfcpy.conf"

if [ -e "$modprobe_file" ]; then
    sudo rm -f "$modprobe_file"
fi
if lsmod | grep "pn533_usb"; then
    sudo rmmod pn533_usb 2>/dev/null
    sudo sh -c "echo 'install pn533_usb /bin/true' >> $modprobe_file"
fi

if lsmod | grep "port100"; then
    sudo rmmod port100 2>/dev/null
    sudo sh -c "echo 'install port100 /bin/true' >> $modprobe_file"
fi

udev_file="/etc/udev/rules.d/50-usb-nfc-rule.rules"

usb_devices=$(lsusb | sed -e 's/.*ID \([a-f0-9]\+:[a-f0-9]\+\).*/\1/g')

valid_device_ids=($(python -c "import nfc.clf.device; [print('%04x:%04x' % x) for x in nfc.clf.device.usb_device_map.keys()]"))

if [ -e "$udev_file" ]; then
    sudo rm -f "$udev_file"
fi
for dev in $usb_devices; do
    if echo ${valid_device_ids[@]} | grep -woq $dev; then
        #$dev is in valid id array
        VID="${dev%%:*}"
        PID="${dev#*:}"
        sudo sh -c "echo 'SUBSYSTEM==\"usb\", ATTRS{idVendor}==\"$VID\", ATTRS{idProduct}==\"$PID\", GROUP=\"plugdev\"' >> $udev_file"
    fi
done
sudo udevadm control --reload-rules
sudo udevadm trigger

sudo gpasswd -a $CURRENT_USER plugdev
sudo gpasswd -a $CURRENT_USER dialout
sudo gpasswd -a $CURRENT_USER tty