# CLI Client

The CLI (command line interface) client can be used to send [RPC commands](./rpc-commands.md) from command line to Phoniebox.

## Installation

* Install prerequisites: `sudo apt-get install libczmq-dev`
* Change to directory: `cd ~/RPi-Jukebox-RFID/src/cli_client`
* Compile CLI client: `gcc pbc.c -o pbc -lzmq -Wall`

## Usage

* Get help info: `./pbc -h`
* Example shutdown: `./pbc -p host -o shutdown`

See also [RPC Commands](./rpc-commands.md) reference.

## Reference

* <https://zeromq.org/>
* <https://www.jsonrpc.org/specification>
