#!/usr/bin/env python
"""
Command Line Interface to the Jukebox RPC Server

A command line tool for sending RPC commands to the running jukebox app.
This uses the same interface as the WebUI. Can be used for additional control
or for debugging.

The tool features auto-completion and command history.
Now supports quoted arguments for handling spaces in arguments.

The list of available commands is fetched from the running Jukebox service.
"""

import argparse
import zmq
import curses
import curses.ascii
import jukebox.rpc.client as rpc
import shlex  # Added for proper command parsing

url: str
client: rpc.RpcClient
rpc_help = {}
candidates = []
history = ['']
prompt = '> '


def add_cli():
    global rpc_help
    rpc_help["help"] = {'description': "Print RPC Server command list (all commands that start with ...)",
                        'signature': "(cmd_starts_with='')"}
    rpc_help['usage'] = {'description': "Usage help and key bindings", 'signature': "()"}
    rpc_help['exit'] = {'description': "Exit RPC Client", 'signature': "()"}


def get_help(scr):
    global rpc_help
    global candidates
    rpc_help = {}
    try:
        rpc_help_tmp = client.enque('misc', 'rpc_cmd_help')
    except Exception:
        scr.addstr("\n\n" + '-' * 70 + "\n")
        scr.addstr("Could not reach RPC Server. Jukebox running? Correct Port?\n")
        scr.addstr('-' * 70 + "\n\n")
        scr.refresh()
    else:
        # Sort the commands (Python 3.7 has ordered entries in dicts!)
        rpc_help = {k: rpc_help_tmp[k] for k in sorted(rpc_help_tmp.keys())}
    add_cli()
    candidates = rpc_help.keys()


def format_help(scr, topic):
    global rpc_help
    # Always update help, in case Jukebox App has been restarted in between
    scr.erase()
    get_help(scr)
    max_y, max_x = scr.getmaxyx()
    scr.addstr("Available commands:\n\n")
    for key, value in rpc_help.items():
        sign: str = value['signature']
        sign = sign[sign.find('('):]
        func = f"{key}{sign}"
        if key.startswith(topic):
            scr.addstr(f"{func:50}: {value['description']}\n")
        [y, x] = scr.getyx()
        if y == max_y - 1:
            scr.addstr("--HIT A KEY TO CONTINUE--")
            scr.getch()
            scr.erase()
    scr.addstr("\n")
    scr.refresh()


def format_welcome(scr):
    scr.addstr("\n\n" + '-' * 70 + "\n")
    scr.addstr("RPC Tool\n")
    scr.addstr('-' * 70 + "\n")
    scr.addstr(f"Connection url: '{client.address}'\n")
    try:
        jukebox_version = client.enque('misc', 'get_version')
    except Exception:
        jukebox_version = "unknown"
    scr.addstr(f"Jukebox version: {jukebox_version}\n")
    scr.addstr(f"Pyzmq version: {zmq.pyzmq_version()}; ZMQ version: {zmq.zmq_version()}; has draft API: {zmq.DRAFT_API}\n")
    scr.addstr('-' * 70 + "\n")


def format_usage(scr):
    scr.addstr("\n\nUsage:\n")
    scr.addstr("  > cmd [arg1] [arg2] [arg3]\n")
    scr.addstr("e.g.\n")
    scr.addstr('  > volume.ctrl.set_volume 50\n')

    # General content playback examples (for webapp/CLI)
    scr.addstr("\nPlaying content (using play_content):\n")
    scr.addstr('  > player.ctrl.play_content \'{"artist":"Pink Floyd","album":"The Wall"}\' album\n')
    scr.addstr('  > player.ctrl.play_content "/music/classical" folder true\n')
    scr.addstr('  > player.ctrl.play_content "/music/favorites/track.mp3" single\n')

    # RFID card specific examples
    scr.addstr("\nPlaying content with card behavior (using play_card):\n")
    scr.addstr('  > player.ctrl.play_card \'{"artist":"Pink Floyd","album":"The Wall"}\' album false toggle\n')
    scr.addstr('  > player.ctrl.play_card "/music/classical" folder true replay\n')
    scr.addstr('  > player.ctrl.play_card "/music/stories" folder false none\n')

    scr.addstr("\n")
    scr.addstr("Quoting:\n")
    scr.addstr("  - Use single quotes (\') for JSON content\n")
    scr.addstr('  - Use double quotes (") for simple string arguments containing spaces\n')
    scr.addstr('  - Escape quotes within quoted strings with \\\n')
    scr.addstr("\n")
    scr.addstr("Content Types:\n")
    scr.addstr("  - album: requires JSON with artist and album\n")
    scr.addstr("  - single: direct path to audio file\n")
    scr.addstr("  - folder: path to folder (optional recursive flag)\n")
    scr.addstr("\n")
    scr.addstr("Second Swipe Actions (for play_card):\n")
    scr.addstr("  - none: disable second swipe\n")
    scr.addstr("  - toggle: toggle play/pause\n")
    scr.addstr("  - play: start playing\n")
    scr.addstr("  - skip: next track\n")
    scr.addstr("  - rewind: restart playlist\n")
    scr.addstr("  - replay: restart folder\n")
    scr.addstr("  - replay_if_stopped: restart if stopped\n")
    scr.addstr("\n")
    scr.addstr("Use <TAB> for auto-completion of commands!\n")
    scr.addstr("Use <UP>/<DOWN> for command history!\n")
    scr.addstr("\n")
    scr.addstr("Type help <RET>, to get a list of all commands'\n")
    scr.addstr("Type usage <RET>, to get this usage help'\n")
    scr.addstr("\n")
    scr.addstr("After Jukebox app restart, call help once to update command list from jukebox app\n")
    scr.addstr("\n")
    scr.addstr("To exit, press Ctrl-D or type 'exit'\n")
    scr.addstr("\n")
    scr.refresh()


def get_common_beginning(strings):
    """
    Return the strings that are common to the beginning of each string in the strings list.
    """
    result = []
    limit = min([len(s) for s in strings])
    for i in range(limit):
        chs = set([s[i] for s in strings])
        if len(chs) == 1:
            result.append(chs.pop())
        else:
            break
    return ''.join(result)


def autocomplete(msg):
    matches = [s for s in candidates if s.startswith(msg)]
    if len(matches) == 0:
        return msg, matches
    common = get_common_beginning(matches)
    return common, matches


def is_printable(ch: int):
    return 32 <= ch <= 127


def reprompt(scr, msg, y, x):
    scr.move(y, 0)
    scr.clrtoeol()
    scr.addstr(prompt)
    scr.addstr(msg)
    scr.move(y, x)


def get_input(scr):
    curses.noecho()
    ch = 0
    msg = ''
    ihist = ''
    hidx = len(history)
    [y, x] = scr.getyx()
    reprompt(scr, msg, y, len(prompt) + len(msg))
    scr.refresh()

    # Track if we're inside quotes
    in_quotes = False
    escape_next = False

    while ch != ord(b'\n'):
        try:
            ch = scr.getch()
        except KeyboardInterrupt:
            msg = 'exit'
            break
        [y, x] = scr.getyx()
        pos = x - len(prompt)

        if ch == ord(b'\t') and not in_quotes:
            msg, matches = autocomplete(msg)
            if len(matches) > 1:
                scr.addstr('\n')
                scr.addstr(', '.join(matches))
                scr.addstr('\n')
            scr.clrtobot()
            reprompt(scr, msg, y, len(prompt) + len(msg))
        elif ch == ord(b'\n'):
            # Only accept newline if we're not in the middle of a quote
            if not in_quotes:
                break
            else:
                # Add the newline to multi-line quoted string
                msg = msg[0:pos] + "\\n" + msg[pos:]
                reprompt(scr, msg, y, x + 2)
        elif ch == 4 and not in_quotes:
            msg = 'exit'
            break
        elif ch == curses.KEY_BACKSPACE or ch == 127:
            if pos > 0:
                # Handle backspace in quotes - need to check if we're deleting a quote char
                if msg[pos-1] == '"' and not escape_next:
                    in_quotes = not in_quotes
                elif msg[pos-1] == '\\':
                    escape_next = False
                scr.delch(y, x - 1)
                msg = msg[0:pos - 1] + msg[pos:]
        elif ch == curses.KEY_DC:
            if pos < len(msg):
                if msg[pos] == '"' and not escape_next:
                    in_quotes = not in_quotes
                scr.delch(y, x)
                msg = msg[0:pos] + msg[pos + 1:]
        elif ch == curses.KEY_LEFT:
            if pos > 0:
                scr.move(y, x - 1)
        elif ch == curses.KEY_RIGHT:
            if pos < len(msg):
                scr.move(y, x + 1)
        elif ch == curses.KEY_HOME:
            scr.move(y, len(prompt))
        elif ch == curses.KEY_END:
            scr.move(y, len(prompt) + len(msg))
        elif ch == curses.KEY_UP and not in_quotes:
            if hidx == len(history):
                ihist = msg
            hidx = max(hidx - 1, 0)
            msg = history[hidx]
            reprompt(scr, msg, y, len(prompt) + len(msg))
        elif ch == curses.KEY_DOWN and not in_quotes:
            hidx = min(hidx + 1, len(history))
            if hidx == len(history):
                msg = ihist
            else:
                msg = history[hidx]
            reprompt(scr, msg, y, len(prompt) + len(msg))
        elif is_printable(ch):
            char = curses.ascii.unctrl(ch)
            if char == '"' and not escape_next:
                in_quotes = not in_quotes
            elif char == '\\':
                escape_next = True
            else:
                escape_next = False
            msg = msg[0:pos] + char + msg[pos:]
            reprompt(scr, msg, y, x + 1)

        scr.refresh()

    scr.refresh()
    if msg:
        history.append(msg)
    return msg


def parse_command(cmd_str):
    """
    Parse command string using shlex to handle quoted arguments properly.
    Returns (command_parts, args) tuple.
    """
    try:
        parts = shlex.split(cmd_str)
        if not parts:
            return [], []

        # Split the command on dots for package.plugin.method
        cmd_parts = [v for v in parts[0].split('.') if v]

        # Convert args to appropriate types
        args = [tonum(arg) for arg in parts[1:]]

        return cmd_parts, args
    except ValueError as e:
        # Handle unclosed quotes
        return None, str(e)


def tonum(string_value):
    """Convert string to number if possible, otherwise return original string."""
    ret = string_value
    try:
        ret = int(string_value)
    except ValueError:
        pass
    else:
        return ret
    try:
        ret = float(string_value)
    except ValueError:
        pass
    else:
        return ret
    if string_value.isalnum() and string_value.startswith('0x'):
        try:
            ret = int(string_value, base=16)
        except ValueError:
            pass
        else:
            return ret
    return ret


def main(scr):
    global candidates
    scr.idlok(True)
    scr.scrollok(True)
    format_welcome(scr)
    get_help(scr)
    format_usage(scr)
    cmd = ''
    while cmd != 'exit':
        cmd = get_input(scr)
        scr.addstr("\n")

        if cmd == '':
            continue

        # Handle built-in commands
        if cmd.startswith('help'):
            topic = ''
            try:
                _, args = parse_command(cmd)
                if args:
                    topic = args[0]
            except:
                pass
            format_help(scr, topic)
            continue
        elif cmd == 'usage':
            format_usage(scr)
            continue
        elif cmd == 'exit':
            break

        # Parse the command
        cmd_parts, args = parse_command(cmd)

        if isinstance(args, str):
            scr.addstr(f"Error parsing command: {args}\n")
            continue

        if not (2 <= len(cmd_parts) <= 3):
            scr.addstr("Error: Invalid command format. Use: package.plugin.method or package.plugin\n")
            continue

        method = cmd_parts[2] if len(cmd_parts) == 3 else None

        try:
            response = client.enque(cmd_parts[0], cmd_parts[1], method, args=args)
            scr.addstr(f"\n:: Response =\n{response}\n\n")
        except zmq.error.Again:
            scr.addstr("\n\n" + '-' * 70 + "\n")
            scr.addstr("Could not reach RPC Server. Jukebox running? Correct Port?\n")
            scr.addstr('-' * 70 + "\n\n")
        except Exception as e:
            scr.addstr(f":: Error: {str(e)}\n")


def runcmd(cmd):
    """Run a single command and exit."""
    cmd_parts, args = parse_command(cmd)

    if isinstance(args, str):
        print(f"Error parsing command: {args}")
        return

    if not (2 <= len(cmd_parts) <= 3):
        print("Error: Invalid command format. Use: package.plugin.method or package.plugin")
        return

    method = cmd_parts[2] if len(cmd_parts) == 3 else None

    try:
        response = client.enque(cmd_parts[0], cmd_parts[1], method, args=args)
        print(f"\n:: Response =\n{response}\n")
    except zmq.error.Again:
        print("\n\n" + '-' * 70)
        print("Could not reach RPC Server. Jukebox running? Correct Port?")
        print('-' * 70 + "\n")
    except Exception as e:
        print(f":: Error: {str(e)}")


if __name__ == '__main__':
    default_tcp = 5555
    default_ws = 5556
    url = f"tcp://localhost:{default_tcp}"
    argparser = argparse.ArgumentParser(description='The Jukebox RPC command line tool',
                                      epilog=f'Default connection: {url}')
    port_group = argparser.add_mutually_exclusive_group()
    port_group.add_argument("-w", "--websocket",
                           help=f"Use websocket protocol on PORT [default: {default_ws}]",
                           nargs='?', const=default_ws,
                           metavar="PORT", default=None)
    port_group.add_argument("-t", "--tcp",
                           help=f"Use tcp protocol on PORT [default: {default_tcp}]",
                           nargs='?', const=default_tcp,
                           metavar="PORT", default=None)
    port_group.add_argument("-c", "--command",
                           help="Send command to Jukebox server",
                           default=None)
    args = argparser.parse_args()

    if args.websocket is not None:
        url = f"ws://localhost:{args.websocket}"
    elif args.tcp is not None:
        url = f"tcp://localhost:{args.tcp}"

    print(f">>> RPC Client connect on {url}")

    client = rpc.RpcClient(url)

    if args.command is not None:
        runcmd(args.command)
        exit(0)
    else:
        curses.wrapper(main)

    print(">>> RPC Client exited!")
