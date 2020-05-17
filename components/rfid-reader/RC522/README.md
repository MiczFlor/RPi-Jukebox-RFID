# How to setup the RC522 RFID reader

1. Install Python dependencies
   - `sudo python3 -m pip install -q -r <phoniebox_dir>/components/rfid-reader/RC522/requirements.txt`

2. Configure experimental reader
   - `cd <phoniebox_dir>/scripts`
   - `cp Reader.py.experimental Reader.py`
   - Run `python3 RegisterDevice.py`
   - Select 0 (MFRC522)

3. Restart the phoniebox-rfid-reader service:
   - `sudo systemctl restart phoniebox-rfid-reader.service`