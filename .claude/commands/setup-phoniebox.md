# /setup-phoniebox

Set up a Phoniebox RFID jukebox on a Raspberry Pi. Walk the user through hardware, OS flashing, SSH, installation, RFID reader registration, audio management, and card linking — handling all remote work automatically via SSH.

## What this skill does
- Guides user through flashing Raspberry Pi OS and SSH configuration
- Establishes passwordless SSH key authentication
- Installs Phoniebox v2 non-interactively
- Detects and registers the USB RFID reader
- Downloads audio from YouTube via yt-dlp
- Links RFID cards to audio folders or system commands
- Fixes common issues: evdev missing, volume normalization, startup volume, udev auto-restart

---

## Step 1 — Hardware checklist

Ask the user to confirm they have:
- Raspberry Pi (2/3/4 or Zero W) — recommend 3B+
- MicroSD card (16GB+, Class 10)
- USB RFID reader (125kHz plug-and-play recommended)
- RFID cards/fobs (must match reader frequency)
- USB-powered speakers
- Power supply for Pi
- Ethernet cable (recommended for installation, WiFi optional after)

Ask which Raspberry Pi model they have. Ask if they want Spotify (Premium required) or local audio only.

---

## Step 2 — Flash the SD card

Tell the user to download Raspberry Pi Imager from https://www.raspberrypi.com/software/

**Imager settings (exact values matter):**
- Device: their Pi model
- OS: Raspberry Pi OS Lite (32-bit) — **Legacy Bullseye**, NOT Bookworm
- Customisation:
  - Hostname: `phoniebox`
  - Username: `pi` (REQUIRED — Phoniebox installer only supports user `pi`)
  - Password: `raspberry`
  - SSH: **Allow password authentication**
  - WiFi: their network (optional — Ethernet is more reliable for setup)

Warn: if they set username to anything other than `pi`, the installer will fail with "User must be 'pi'".

---

## Step 3 — Set up SSH key authentication

Check for existing SSH keys:
```bash
ls ~/.ssh/id_ed25519.pub
```

If missing, generate one:
```bash
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519 -N ""
```

Show the public key to the user:
```bash
cat ~/.ssh/id_ed25519.pub
```

Find the Pi's IP address:
```bash
arp -a | grep -i "b8-27-eb\|dc-a6-32\|e4-5f-01"
```

If not found via arp, ask user to check router or try `ping phoniebox.local`.

Once IP is known (e.g. 192.168.0.167), copy the key using Python paramiko (since sshpass is often unavailable on Windows):

```python
import paramiko
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('PI_IP', username='pi', password='raspberry', timeout=10)
pubkey = open('~/.ssh/id_ed25519.pub').read().strip()
for cmd in ['mkdir -p ~/.ssh', 'chmod 700 ~/.ssh',
            f'echo "{pubkey}" >> ~/.ssh/authorized_keys',
            'chmod 600 ~/.ssh/authorized_keys']:
    stdin, stdout, stderr = client.exec_command(cmd)
    stdout.channel.recv_exit_status()
client.close()
```

If paramiko is not installed: `pip install paramiko`

Verify key auth works:
```bash
ssh -o StrictHostKeyChecking=no -i ~/.ssh/id_ed25519 pi@PI_IP "echo connected"
```

Store the Pi's IP for all subsequent steps. Use this SSH command pattern for all remote work:
```bash
ssh -o StrictHostKeyChecking=no -i ~/.ssh/id_ed25519 pi@PI_IP "COMMAND"
```

---

## Step 4 — Install Phoniebox

Install git if missing:
```bash
ssh pi@PI_IP "sudo apt-get install -y git"
```

Clone the repository:
```bash
ssh pi@PI_IP "cd /home/pi && git clone https://github.com/MiczFlor/RPi-Jukebox-RFID.git"
```

Create non-interactive install config:
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

Run the installer in the background and tail the log:
```bash
ssh pi@PI_IP "nohup sudo bash /home/pi/RPi-Jukebox-RFID/scripts/installscripts/install-jukebox.sh -a > /home/pi/install.log 2>&1 &"
```

Monitor progress (check every 2-3 minutes):
```bash
ssh pi@PI_IP "tail -20 /home/pi/install.log && ps aux | grep install-jukebox | grep -v grep"
```

Installation is complete when log shows `Done (in Xh Xm Xs)`. Then reboot:
```bash
ssh pi@PI_IP "sudo reboot"
```

Wait for Pi to come back up:
```bash
until ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 -i ~/.ssh/id_ed25519 pi@PI_IP "echo up" 2>/dev/null; do sleep 3; done
```

---

## Step 5 — Fix common post-install issues

### Install missing evdev module
```bash
ssh pi@PI_IP "sudo pip3 install evdev --break-system-packages"
```

### Fix volume settings
Disable MPD volume normalization:
```bash
ssh pi@PI_IP "sudo sed -i 's/volume_normalization.*\"yes\"/volume_normalization\t\t\"no\"/' /etc/mpd.conf && sudo systemctl restart mpd"
```

Set startup volume to 85:
```bash
ssh pi@PI_IP "echo '85' > /home/pi/RPi-Jukebox-RFID/settings/Startup_Volume"
```

Set PCM to 100% on every boot:
```bash
ssh pi@PI_IP "sudo tee /etc/rc.local << 'EOF'
#!/bin/sh -e
amixer set PCM 100%
exit 0
EOF
sudo chmod +x /etc/rc.local"
```

### Fix audio folder permissions
```bash
ssh pi@PI_IP "sudo chown -R pi:www-data /home/pi/RPi-Jukebox-RFID/shared/audiofolders/ && sudo chmod -R 775 /home/pi/RPi-Jukebox-RFID/shared/audiofolders/"
```

---

## Step 6 — Set up RFID reader

Check if reader is detected:
```bash
ssh pi@PI_IP "lsusb && ls /dev/input/by-id/"
```

Get the exact device name (important — must match exactly, no trailing newline):
```bash
ssh pi@PI_IP "python3 -c 'from evdev import InputDevice, list_devices; [print(repr(InputDevice(fn).name)) for fn in list_devices()]'"
```

Write device name without trailing newline:
```bash
ssh pi@PI_IP "printf 'DEVICE_NAME_HERE' > /home/pi/RPi-Jukebox-RFID/scripts/deviceName.txt"
```

**Common issue:** `deviceName.txt` with a trailing `\n` causes "Could not find device" error. Always use `printf` not `echo` to write this file.

Restart RFID service:
```bash
ssh pi@PI_IP "sudo systemctl restart phoniebox-rfid-reader.service"
```

Test card reading (swipe card during the 15-second window):
```bash
ssh pi@PI_IP "python3 -c '
from evdev import InputDevice, list_devices
from select import select
devices = [InputDevice(fn) for fn in list_devices()]
for d in devices:
    if \"Sycreader\" in d.name or \"RFID\" in d.name:
        print(\"Swipe card now!\")
        r,w,x = select([d], [], [], 15)
        if r:
            for event in d.read(): print(event)
'"
```

### Set up udev rule for auto-restart on USB reconnect

Get the vendor and product ID:
```bash
ssh pi@PI_IP "lsusb | grep -i rfid"
```

Create udev rule (replace VENDOR and PRODUCT with hex IDs from lsusb):
```bash
ssh pi@PI_IP "sudo tee /etc/udev/rules.d/99-rfid-reader.rules << 'EOF'
ACTION==\"add\", SUBSYSTEM==\"usb\", ATTRS{idVendor}==\"VENDOR\", ATTRS{idProduct}==\"PRODUCT\", RUN+=\"/bin/systemctl restart phoniebox-rfid-reader.service\"
EOF
sudo udevadm control --reload-rules"
```

---

## Step 7 — Download audio from YouTube

Install Node.js (required for yt-dlp JS challenge solving):
```bash
ssh pi@PI_IP "sudo apt-get install -y nodejs"
```

Create a folder and download audio:
```bash
ssh pi@PI_IP "mkdir -p /home/pi/RPi-Jukebox-RFID/shared/audiofolders/FOLDER_NAME && yt-dlp --js-runtimes node --remote-components ejs:github -x --audio-format mp3 --audio-quality 0 -o '/home/pi/RPi-Jukebox-RFID/shared/audiofolders/FOLDER_NAME/%(title)s.%(ext)s' 'YOUTUBE_URL'"
```

Fix permissions after download:
```bash
ssh pi@PI_IP "sudo chown -R pi:www-data /home/pi/RPi-Jukebox-RFID/shared/audiofolders/ && sudo chmod -R 775 /home/pi/RPi-Jukebox-RFID/shared/audiofolders/"
```

Use English folder names — Hebrew/special characters can cause issues with the web interface.

---

## Step 8 — Register RFID cards

Check latest swiped card:
```bash
ssh pi@PI_IP "cat /home/pi/RPi-Jukebox-RFID/shared/latestID.txt"
```

Link a card to an audio folder (write folder name without trailing newline):
```bash
ssh pi@PI_IP "printf 'FOLDER_NAME' > /home/pi/RPi-Jukebox-RFID/shared/shortcuts/CARD_ID"
```

Link a card to a system command (stop, volume up/down, shutdown, etc.):

Edit `/home/pi/RPi-Jukebox-RFID/settings/rfid_trigger_play.conf` and replace the placeholder with the card ID. Example for stop:
```bash
ssh pi@PI_IP "sed -i 's/CMDSTOP=\"%CMDSTOP%\"/CMDSTOP=\"CARD_ID\"/' /home/pi/RPi-Jukebox-RFID/settings/rfid_trigger_play.conf"
```

Available commands: CMDSTOP, CMDPAUSE, CMDPLAY, CMDVOLUP, CMDVOLDOWN, CMDNEXT, CMDPREV, CMDSHUFFLE, CMDSHUTDOWN, CMDREBOOT, CMDMUTE, CMDVOL30–100

---

## Step 9 — Verify everything works

Run full health check:
```bash
ssh pi@PI_IP "
echo '=== RFID Service ===' && sudo systemctl is-active phoniebox-rfid-reader.service
echo '=== Volume ===' && amixer get PCM | grep Mono
echo '=== MPD Volume ===' && /home/pi/RPi-Jukebox-RFID/scripts/playout_controls.sh -c=getvolume
echo '=== Audio Folders ===' && ls /home/pi/RPi-Jukebox-RFID/shared/audiofolders/
echo '=== Registered Cards ===' && for f in /home/pi/RPi-Jukebox-RFID/shared/shortcuts/*; do echo \"\$(basename \$f): \$(cat \$f)\"; done
"
```

Check web interface is accessible: `http://phoniebox.local` or `http://PI_IP`

---

## Troubleshooting

**"User must be 'pi'" error during install**
Re-flash SD card with username `pi` exactly.

**SSH "Permission denied"**
- Password auth disabled: run `sudo nano /etc/ssh/sshd_config`, set `PasswordAuthentication yes`, restart ssh
- Wrong password: run `sudo passwd pi` on the Pi directly (connect monitor + keyboard)
- PAM issue: run `sudo passwd pi` to reset password

**RFID reader not detected**
- Try different USB port
- Use powered USB hub (Pi 3B+ may not supply enough power)
- Check `lsusb` — reader must appear before registration

**"Could not find device" in RFID service**
- Run `python3 -c 'from evdev import InputDevice, list_devices; [print(repr(InputDevice(fn).name)) for fn in list_devices()]'`
- Write exact name using `printf` (not `echo`) to avoid trailing newline

**Audio folder not visible in web interface**
- Fix permissions: `sudo chown -R pi:www-data /home/pi/RPi-Jukebox-RFID/shared/audiofolders/`
- Use English folder names

**Volume starts loud then gets quiet**
- Disable MPD normalization: set `volume_normalization "no"` in `/etc/mpd.conf`

**Card registered but doesn't play**
- Check shortcuts file contains folder name, not card ID: `cat /home/pi/RPi-Jukebox-RFID/shared/shortcuts/CARD_ID`
- Fix with: `printf 'FOLDER_NAME' > /home/pi/RPi-Jukebox-RFID/shared/shortcuts/CARD_ID`
