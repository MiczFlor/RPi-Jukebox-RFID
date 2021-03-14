# How to setup the PC/SC RFID readers

[PC/SC](https://en.wikipedia.org/wiki/PC/SC) PC/SC (short for "Personal Computer/Smart Card") is a specification for smart-card integration into computing environments.

* https://github.com/MiczFlor/RPi-Jukebox-RFID/pull/1250
* https://github.com/MiczFlor/RPi-Jukebox-RFID/issues/533

## Install

1. **You can use the `setup_PCSCreader.sh` script (recommended)** or follow the manual steps:

2. Install Python dependencies
   - `sudo python3 -m pip install -q -r <phoniebox_dir>/components/rfid-reader/PC-SC/requirements.txt`

3. Configure experimental reader
   - `cd <phoniebox_dir>/scripts`
   - `cp Reader.py.pcsc Reader.py`
   - Run `python3 RegisterDevice.py`
   - Select your RFID reader

4. Restart the phoniebox-rfid-reader service:
   - `sudo systemctl restart phoniebox-rfid-reader.service`
