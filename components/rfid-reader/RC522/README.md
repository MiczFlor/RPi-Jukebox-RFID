# RC522 Reader

## How to setup the RC522 RFID reader

1. **You can use the `setup_rc522.sh` script (recommended)** or follow the manual steps:

2. Install Python dependencies
   - `sudo python3 -m pip install -q -r <phoniebox_dir>/components/rfid-reader/RC522/requirements.txt`

3. Configure experimental reader
   - `cd <phoniebox_dir>/scripts`
   - `cp Reader.py.experimental Reader.py`
   - Run `python3 RegisterDevice.py`
   - Select 0 (MFRC522)

4. Restart the phoniebox-rfid-reader service:
   - `sudo systemctl restart phoniebox-rfid-reader.service`

Be aware that unlike a few other installations with this card reader the phoniebox requires the IRQ pin to be connected (on the raspberry pi and zero normaly to GPIO 24 or PIN 18).

## Working cards/tags

Cards or tags must support 13.56 MHz. Currently, only cards/tags of the type "NXP Mifare Classic 1k(S50)", "NXP Mifare Classic 4k(S70)" and "NXP Mifare Ultralight (C)" can be used. Type "NXP Mifare NTAG2xx" will not work!
