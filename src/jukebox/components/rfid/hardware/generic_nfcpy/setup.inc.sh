#!/usr/bin/env bash

modprobe_file="/etc/modprobe.d/disable_driver_jukebox_nfcpy.conf"


if lsmod | grep "pn533_usb"; then
    sudo rmmod pn533_usb 2>/dev/null
    sudo sh -c "echo 'install pn533_usb /bin/true' >> $modprobe_file"
fi

if lsmod | grep "port100"; then
    sudo rmmod port100 2>/dev/null
    sudo sh -c "echo 'install v /bin/true' >> $modprobe_file"
fi

udev_file="/etc/udev/rules.d/50-usb-nfc-rule.rules"

usb_devices=$(lsusb | sed -e 's/.*ID \([a-f0-9]\+:[a-f0-9]\+\).*/\1/g')

valid_device_ids=(
    "054c:02e1"
    "054c:06c1"
    "054c:06c3"
    "054c:0193"
    "04cc:0531"
    "04cc:2533"
    "072f:2200"
    "04e6:5591"
    "04e6:5593"
)

for dev in $usb_devices; do
    if echo ${valid_device_ids[@]} | grep -woq $dev; then
        #$dev is in valid id array
        VID="${dev%%:*}"
        PID="${dev#*:}"
        sudo sh -c "echo 'SUBSYSTEM==\"usb\", ATTRS{idVendor}==\"$VID\", ATTRS{idProduct}==\"$PID\", MODE=\"0666\"' >> $udev_file"
    fi
done
sudo udevadm control --reload-rules
sudo udevadm trigger

sudo gpasswd -a pi dialout
sudo gpasswd -a pi tty