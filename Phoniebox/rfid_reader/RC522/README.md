# How to setup the RC522 RFID reader

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
