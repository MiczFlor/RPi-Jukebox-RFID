# HiFiBerry

## Automatic setup

Use this install script to enable your HiFiBerry board.

```
$ cd; cd ~/RPi-Jukebox-RFID/installation/components && chmod +x setup-hifiberry.sh && sudo ./setup_hifiberry.sh
```

## Manual steps to enable sound through HiFiBerry board

1. Make sure your onboard sound of your Raspberry Pi is disabled. Check `/boot/config.txt`. The installation

    ```
    dtparam=audio=off
    ```

2. Run the following command to enable HiFiBerry boards.

    ```
    echo "dtoverlay=hifiberry-dac" | sudo tee -a /boot/config.txt
    ```

3. Enable volume control. Create or edit the following file: `sudo vi /etc/asound.conf`

    ```
    pcm.hifiberry {
        type softvol
        slave.pcm "plughw:0"
        control.name "HifiBerry"
        control.card 0
    }

    pcm.!default {
        type plug
        slave.pcm "hifiberry"
    }
    ```

4. Restart your device.
