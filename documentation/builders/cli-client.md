# RPC CLI Client

The Python CLI (Command Line Interface) client can be used to send [RPC commands](./rpc-commands.md) to Phoniebox. It provides an interactive shell with autocompletion and command history, as well as direct command execution.

The RPC tool can be found here:

```bash
~/RPi-Jukebox-RFID/src/jukebox/run_rpc_tool.py
```

## Usage

The CLI tool can be used in two modes:

### Interactive Mode

```bash
# Start interactive shell
./run_rpc_tool.py

# Start with specific connection type
./run_rpc_tool.py --tcp 5555     # TCP connection on port 5555
./run_rpc_tool.py --websocket    # WebSocket connection on default port
```

In interactive mode:

- Use TAB for command autocompletion
- Use UP/DOWN arrows for command history
- Type `help` to see available commands
- Type `usage` for detailed usage information
- Press Ctrl-D or type `exit` to quit

### Direct Command Mode

```bash
# Execute single command
./run_rpc_tool.py -c 'command [args...] [key=value...]'

# Examples with positional args:
./run_rpc_tool.py -c 'volume.ctrl.set_volume 50'
./run_rpc_tool.py -c 'player.ctrl.play_content "/music/test.mp3" single'

# Examples with kwargs:
./run_rpc_tool.py -c 'volume.ctrl.set_volume level=50'
./run_rpc_tool.py -c 'player.ctrl.play_content content="/music/test.mp3" content_type=single'
```

## Command Format

Commands support both positional arguments and keyword arguments:

```python
package.plugin.method [arg1] [arg2] [arg3]          # Positional args
package.plugin.method [key1=value1] [key2=value2]   # Keyword args
```

Arguments can be:

- Numbers (50 or level=50)
- Strings (use quotes for spaces: "my string" or path="my string")
- JSON objects (use single quotes: '{"key":"value"}')
- Hexadecimal numbers (prefix with 0x: 0xFF or value=0xFF)

### Examples

```bash
# Simple commands - both styles work
volume.ctrl.set_volume 50
volume.ctrl.set_volume level=50

system.ctrl.shutdown

# Playing content - positional args
player.ctrl.play_content '{"artist":"Pink Floyd","album":"The Wall"}' album
player.ctrl.play_content "/music/classical" folder true
player.ctrl.play_content "/music/track.mp3" single

# Playing content - keyword args
player.ctrl.play_content content='{"artist":"Pink Floyd","album":"The Wall"}' content_type=album
player.ctrl.play_content content="/music/classical" content_type=folder recursive=true
player.ctrl.play_content content="/music/track.mp3" content_type=single

# Reader-based playback - positional args
player.ctrl.play_from_reader '{"artist":"Pink Floyd","album":"The Wall"}' album false toggle
player.ctrl.play_from_reader "/music/classical" folder true replay

# Reader-based playback - keyword args
player.ctrl.play_from_reader content='{"artist":"Pink Floyd","album":"The Wall"}' content_type=album second_swipe=toggle
player.ctrl.play_from_reader content="/music/classical" content_type=folder recursive=true second_swipe=replay
```

## Features

- Command autocompletion
- Command history
- Support for both positional and keyword arguments
- JSON argument support
- Interactive and direct command modes
- Automatic type conversion (strings, numbers, JSON)
- Connection error handling
- Dynamic command help from server
