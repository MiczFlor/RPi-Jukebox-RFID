# Setting Up Phoniebox from Windows

This guide covers the complete Phoniebox v2 setup when your host machine is **Windows**. It addresses all the common pitfalls that don't appear in the standard Linux/Mac instructions.

---

## Prerequisites

- Raspberry Pi 3B+ (recommended), 2, 4, or Zero W
- MicroSD card — 16 GB+, Class 10
- USB RFID reader (125 kHz HID/keyboard-emulation type)
- RFID cards or fobs matching the reader frequency
- USB-powered speakers
- Ethernet cable (strongly recommended for the initial install)

---

## Step 1 — Flash the SD card

Download [Raspberry Pi Imager](https://www.raspberrypi.com/software/) and use these exact settings:

| Setting | Value |
|---|---|
| OS | Raspberry Pi OS Lite **32-bit, Legacy Bullseye** (not Bookworm) |
| Hostname | `phoniebox` |
| Username | `pi` — **mandatory**, the installer rejects any other username |
| Password | `raspberry` |
| SSH | Allow password authentication |
| WiFi | Optional — Ethernet is more reliable during install |

> **Known Raspberry Pi Imager bug on Windows:** In some versions the password is not correctly applied even when entered. If SSH login fails immediately after flashing, connect a monitor and keyboard to the Pi, log in at the console, and run `sudo passwd pi` to reset the password. Also verify that `/etc/ssh/sshd_config` contains `PasswordAuthentication yes` (add it if missing, then `sudo systemctl restart ssh`).

---

## Step 2 — Find the Pi's IP address

After the Pi boots, find its IP from your Windows machine:

```bash
arp -a | findstr "b8-27-eb dc-a6-32 e4-5f-01"
```

Or check your router's DHCP table. You can also try `ping phoniebox.local`.

If you re-flash the SD card and get `WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED`, clear the stale entry:

```bash
ssh-keygen -R phoniebox.local
ssh-keygen -R PI_IP
```

---

## Step 3 — Set up SSH key authentication

Windows does not ship with `sshpass`, so the simplest way to copy your SSH key to the Pi is via Python:

Generate a key if you don't have one:

```bash
ssh-keygen -t ed25519 -f %USERPROFILE%\.ssh\id_ed25519 -N ""
```

Then copy it to the Pi using `paramiko` (install with `pip install paramiko`):

```python
import os
import paramiko

PI_IP = "192.168.x.x"  # replace with your Pi's IP

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(PI_IP, username="pi", password="raspberry", timeout=10)

with open(os.path.expanduser("~/.ssh/id_ed25519.pub")) as f:
    pubkey = f.read().strip()

for cmd in [
    "mkdir -p ~/.ssh",
    "chmod 700 ~/.ssh",
    f'echo "{pubkey}" >> ~/.ssh/authorized_keys',
    "chmod 600 ~/.ssh/authorized_keys",
]:
    stdin, stdout, stderr = client.exec_command(cmd)
    stdout.channel.recv_exit_status()

client.close()
print("Done — passwordless SSH is set up.")
```

Verify it works:

```bash
ssh -o StrictHostKeyChecking=no -i ~/.ssh/id_ed25519 pi@PI_IP "echo connected"
```

---

## Step 4 — Install Phoniebox (non-interactive)

The installer asks a series of interactive questions. To run it unattended, create the config file first:

```bash
ssh pi@PI_IP "cat > /home/pi/PhonieboxInstall.conf << 'EOF'
WIFIconfig=\"NO\"
AUTOHOTSPOTconfig=\"NO\"
EXISTINGuse=\"NO\"
AUDIOiFace=\"PCM\"
DIRaudioFolders=\"/home/pi/RPi-Jukebox-RFID/shared/audiofolders\"
GPIOconfig=\"NO\"
SPOTinstall=\"NO\"
EOF"
```

Clone the repo and launch the installer in the background:

```bash
ssh pi@PI_IP "sudo apt-get install -y git && git clone https://github.com/MiczFlor/RPi-Jukebox-RFID.git"
ssh pi@PI_IP "nohup sudo bash /home/pi/RPi-Jukebox-RFID/scripts/installscripts/install-jukebox.sh -a > /home/pi/install.log 2>&1 &"
```

Monitor progress (installation takes 20–40 minutes):

```bash
ssh pi@PI_IP "tail -20 /home/pi/install.log"
```

The install is complete when the log shows `Done (in Xh Xm Xs)`. Then reboot:

```bash
ssh pi@PI_IP "sudo reboot"
```

---

## Step 5 — Post-install fixes

Run these after the reboot. They address issues that affect nearly every fresh install.

### evdev module missing

The RFID reader service requires `evdev`, which is not always installed automatically:

```bash
ssh pi@PI_IP "sudo pip3 install evdev --break-system-packages"
```

### Volume drops suddenly during playback

MPD's `volume_normalization` is enabled by default and causes the volume to drop a few seconds after playback begins. Disable it:

```bash
ssh pi@PI_IP "sudo sed -i 's/volume_normalization.*\"yes\"/volume_normalization\t\t\"no\"/' /etc/mpd.conf && sudo systemctl restart mpd"
```

### Volume is 0 at startup

```bash
ssh pi@PI_IP "echo '85' > /home/pi/RPi-Jukebox-RFID/settings/Startup_Volume"
```

Set the ALSA PCM channel to 100% on every boot (prevents silent audio after reboot):

```bash
ssh pi@PI_IP "sudo tee /etc/rc.local << 'EOF'
#!/bin/sh -e
amixer set PCM 100%
exit 0
EOF
sudo chmod +x /etc/rc.local"
```

### Audio folders not visible in the web interface

```bash
ssh pi@PI_IP "sudo chown -R pi:www-data /home/pi/RPi-Jukebox-RFID/shared/audiofolders/ && sudo chmod -R 775 /home/pi/RPi-Jukebox-RFID/shared/audiofolders/"
```

---

## Step 6 — Register the USB RFID reader

Check the reader is detected:

```bash
ssh pi@PI_IP "lsusb && ls /dev/input/by-id/"
```

Get the exact device name as reported by evdev:

```bash
ssh pi@PI_IP "python3 -c 'from evdev import InputDevice, list_devices; [print(repr(InputDevice(fn).name)) for fn in list_devices()]'"
```

Write the name to `deviceName.txt` — **use `printf`, never `echo`**. A trailing newline causes a silent mismatch that prevents the service from finding the reader:

```bash
ssh pi@PI_IP "printf 'Sycreader RFID Technology Co., Ltd SYC ID&IC USB Reader' > /home/pi/RPi-Jukebox-RFID/scripts/deviceName.txt"
```

Replace the device name string with the exact output from the command above.

Restart the RFID service:

```bash
ssh pi@PI_IP "sudo systemctl restart phoniebox-rfid-reader.service"
```

### Auto-restart when the reader is unplugged and re-plugged

Get the USB vendor and product IDs:

```bash
ssh pi@PI_IP "lsusb | grep -i rfid"
# example output: Bus 001 Device 004: ID ffff:0035 ...
```

Create the udev rule (replace `VENDOR` and `PRODUCT` with the hex IDs):

```bash
ssh pi@PI_IP "sudo tee /etc/udev/rules.d/99-rfid-reader.rules << 'EOF'
ACTION==\"add\", SUBSYSTEM==\"usb\", ATTRS{idVendor}==\"VENDOR\", ATTRS{idProduct}==\"PRODUCT\", RUN+=\"/bin/systemctl restart phoniebox-rfid-reader.service\"
EOF
sudo udevadm control --reload-rules"
```

---

## Step 7 — Add audio content from YouTube

Install Node.js (required for `yt-dlp` to solve YouTube's JS challenges):

```bash
ssh pi@PI_IP "sudo apt-get install -y nodejs"
```

Create a folder and download audio as MP3:

```bash
ssh pi@PI_IP "mkdir -p /home/pi/RPi-Jukebox-RFID/shared/audiofolders/my-playlist && \
  yt-dlp --js-runtimes node --remote-components ejs:github \
  -x --audio-format mp3 --audio-quality 0 \
  -o '/home/pi/RPi-Jukebox-RFID/shared/audiofolders/my-playlist/%(title)s.%(ext)s' \
  'https://www.youtube.com/watch?v=VIDEO_ID'"
```

Fix permissions after download:

```bash
ssh pi@PI_IP "sudo chown -R pi:www-data /home/pi/RPi-Jukebox-RFID/shared/audiofolders/ && sudo chmod -R 775 /home/pi/RPi-Jukebox-RFID/shared/audiofolders/"
```

> Use English-only folder names — non-ASCII characters can cause display issues in the web interface.

---

## Step 8 — Link RFID cards

Swipe a card, then read its ID:

```bash
ssh pi@PI_IP "cat /home/pi/RPi-Jukebox-RFID/shared/latestID.txt"
```

Link the card to an audio folder — again, use `printf` to avoid a trailing newline:

```bash
ssh pi@PI_IP "printf 'my-playlist' > /home/pi/RPi-Jukebox-RFID/shared/shortcuts/CARD_ID"
```

Link a card to a system command (example: stop playback):

```bash
ssh pi@PI_IP "sed -i 's/CMDSTOP=\"%CMDSTOP%\"/CMDSTOP=\"CARD_ID\"/' /home/pi/RPi-Jukebox-RFID/settings/rfid_trigger_play.conf"
```

Other available commands: `CMDPAUSE`, `CMDPLAY`, `CMDVOLUP`, `CMDVOLDOWN`, `CMDNEXT`, `CMDPREV`, `CMDSHUFFLE`, `CMDSHUTDOWN`, `CMDREBOOT`, `CMDMUTE`, `CMDVOL30`–`CMDVOL100`

---

## Quick health check

```bash
ssh pi@PI_IP "
echo '=== RFID Service ===' && sudo systemctl is-active phoniebox-rfid-reader.service
echo '=== PCM Volume ===' && amixer get PCM | grep Mono
echo '=== Audio Folders ===' && ls /home/pi/RPi-Jukebox-RFID/shared/audiofolders/
echo '=== Registered Cards ===' && for f in /home/pi/RPi-Jukebox-RFID/shared/shortcuts/*; do echo \"\$(basename \$f): \$(cat \$f)\"; done
"
```

Web interface: `http://phoniebox.local` or `http://PI_IP`

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| "User must be 'pi'" during install | Username not set to `pi` in Imager | Re-flash SD card |
| SSH "Permission denied" immediately | Imager bug — password not applied | Connect monitor+keyboard; run `sudo passwd pi`; enable `PasswordAuthentication yes` in sshd_config |
| RFID reader not detected (`lsusb` empty) | USB power issue | Try a different port or a powered USB hub |
| "Could not find device" in RFID service | Trailing newline in `deviceName.txt` | Re-write the file using `printf` (not `echo`) |
| Audio folder invisible in web UI | Wrong file ownership | `sudo chown -R pi:www-data audiofolders/` |
| Volume drops seconds after starting | MPD volume normalization | Set `volume_normalization "no"` in `/etc/mpd.conf` |
| Card swiped but nothing plays | Shortcut file contains card ID instead of folder name | `printf 'FOLDER_NAME' > shortcuts/CARD_ID` |
| RFID service stops after USB reconnect | No auto-restart rule | Create udev rule (Step 6) |
| YouTube download fails | JS challenge / geo-block | Add `--remote-components ejs:github` and install Node.js |
| "Host key changed" warning | Stale known_hosts after re-flash | `ssh-keygen -R phoniebox.local` |
