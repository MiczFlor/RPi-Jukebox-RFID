#!/usr/bin/env python
"""
Command Line Interface to the Jukebox RPC Server

A command line tool for sending RPC commands to the running jukebox app.
Features auto-completion, command history, and RPC command execution.
Supports JSON arguments for complex data structures.
"""

import argparse
import json
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple
import curses
import curses.ascii
import zmq
import jukebox.rpc.client as rpc


@dataclass
class CliState:
    """Encapsulates CLI state and configuration"""
    url: str
    client: rpc.RpcClient
    rpc_help: Dict[str, Dict[str, str]] = None
    candidates: List[str] = None
    history: List[str] = None
    prompt: str = '> '

    def __post_init__(self):
        self.rpc_help = {}
        self.candidates = []
        self.history = ['']


class CommandParser:
    """Handles parsing and execution of RPC commands with JSON and quoted string support"""

    @staticmethod
    def parse_command(cmd: str) -> Tuple[List[str], List[Any], Dict[str, Any]]:
        """
        Parse command string into command parts, positional args, and keyword args
        Returns: (command_parts, args, kwargs)
        """
        # Split while preserving quotes and JSON structures
        parts = CommandParser._split_preserving_json(cmd.strip())
        if not parts:
            return [], [], {}

        # Split cmd on '.' into package.plugin.method
        command_parts = [v for v in parts[0].split('.') if len(v) > 0]

        # Process remaining parts into args and kwargs
        args = []
        kwargs = {}
        seen_keys = set()  # Track seen keyword argument names

        for part in parts[1:]:
            # Check if part is a kwarg (contains '=')
            if '=' in part:
                key, value = part.split('=', 1)
                key = key.strip()
                value = value.strip()

                # Check for duplicate keyword arguments
                if key in seen_keys:
                    raise ValueError(f"Duplicate keyword argument: {key}")
                seen_keys.add(key)

                # Handle the value based on its format
                kwargs[key] = CommandParser._parse_value(value)
            else:
                # Handle as positional argument
                args.append(CommandParser._parse_value(part))

        return command_parts, args, kwargs

    @staticmethod
    def _parse_value(value: str) -> Any:
        """Parse a value string into appropriate type"""
        # Strip quotes if present (only if matching quotes at start and end)
        if (value.startswith('"') and value.endswith('"')) or \
           (value.startswith("'") and value.endswith("'")):
            value = value[1:-1]

        # Try to parse as JSON if it looks like JSON
        if value.startswith('{') or value.startswith('['):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                # If JSON parsing fails, continue with other parsing attempts
                pass

        # Try to convert to number if appropriate
        return CommandParser.convert_to_number(value)

    @staticmethod
    def _split_preserving_json(cmd: str) -> List[str]:  # noqa: C901
        """Split command string while preserving quoted strings and JSON structures"""
        parts = []
        current = []
        brace_count = 0
        bracket_count = 0
        in_single_quotes = False
        in_double_quotes = False
        escape = False

        for char in cmd:
            if escape:
                current.append(char)
                escape = False
                continue

            if char == '\\':
                escape = True
                current.append(char)
                continue

            if char == '"' and not in_single_quotes:
                in_double_quotes = not in_double_quotes
                current.append(char)
                continue

            if char == "'" and not in_double_quotes:
                in_single_quotes = not in_single_quotes
                current.append(char)
                continue

            if not in_single_quotes and not in_double_quotes:
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                elif char == '[':
                    bracket_count += 1
                elif char == ']':
                    bracket_count -= 1
                elif char.isspace() and brace_count == 0 and bracket_count == 0:
                    if current:
                        parts.append(''.join(current))
                        current = []
                    continue

            current.append(char)

        if current:
            parts.append(''.join(current))

        # Validate quote matching
        if in_single_quotes:
            raise ValueError("Unmatched single quote")
        if in_double_quotes:
            raise ValueError("Unmatched double quote")

        return parts

    @staticmethod
    def convert_to_number(value: str) -> Any:
        """Convert string to number if possible"""
        # Try integer
        try:
            return int(value)
        except ValueError:
            pass

        # Try float
        try:
            return float(value)
        except ValueError:
            pass

        # Try hex
        if value.isalnum() and value.startswith('0x'):
            try:
                return int(value, base=16)
            except ValueError:
                pass

        return value


class JukeboxCli:
    """Main CLI class handling user interaction and command execution"""

    def __init__(self, url: str):
        self.state = CliState(url=url, client=rpc.RpcClient(url))
        self.command_parser = CommandParser()

    def update_help(self, scr) -> None:
        """Update available RPC commands from server"""
        try:
            rpc_help_tmp = self.state.client.enque('misc', 'rpc_cmd_help')
            self.state.rpc_help = {k: rpc_help_tmp[k] for k in sorted(rpc_help_tmp.keys())}
        except Exception:
            self._show_connection_error(scr)
            return

        # Add CLI specific commands
        self._add_cli_commands()
        self.state.candidates = list(self.state.rpc_help.keys())

    def _add_cli_commands(self) -> None:
        """Add CLI-specific commands to help"""
        cli_commands = {
            "help": {'description': "Print RPC Server command list (all commands that start with ...)",
                    'signature': "(cmd_starts_with='')"},
            'usage': {'description': "Usage help and key bindings", 'signature': "()"},
            'exit': {'description': "Exit RPC Client", 'signature': "()"}
        }
        self.state.rpc_help.update(cli_commands)

    def execute_command(self, scr, cmd: str) -> None:
        """Execute a command and display results"""
        if not cmd.strip():
            return

        if cmd == 'help':
            self._show_help(scr)
            return
        elif cmd == 'usage':
            self._show_usage(scr)
            return
        elif cmd == 'exit':
            return

        command_parts, args, kwargs = self.command_parser.parse_command(cmd)

        if not (2 <= len(command_parts) <= 3):
            scr.addstr(":: Error = Ill-formatted command\n")
            return

        method = command_parts[2] if len(command_parts) == 3 else None

        try:
            response = self.state.client.enque(
                command_parts[0],
                command_parts[1],
                method,
                args=args,
                kwargs=kwargs
            )
            scr.addstr(f"\n:: Response =\n{response}\n\n")
        except zmq.error.Again:
            self._show_connection_error(scr)
        except Exception as e:
            scr.addstr(f":: Exception response =\n{e}\n")

    def run(self, scr) -> None:
        """Main CLI loop"""
        self._setup_screen(scr)
        self._show_welcome(scr)
        self.update_help(scr)
        self._show_usage(scr)

        cmd = ''
        while cmd != 'exit':
            cmd = self._get_input(scr)
            scr.addstr("\n")
            self.execute_command(scr, cmd)

    def _setup_screen(self, scr) -> None:
        """Configure screen settings"""
        scr.idlok(True)
        scr.scrollok(True)
        curses.noecho()

    def _show_connection_error(self, scr) -> None:
        """Display connection error message"""
        scr.addstr("\n\n" + '-' * 70 + "\n")
        scr.addstr("Could not reach RPC Server. Jukebox running? Correct Port?\n")
        scr.addstr('-' * 70 + "\n\n")
        scr.refresh()

    def _show_welcome(self, scr) -> None:
        """Display welcome message and connection information"""
        scr.addstr("\n\n" + '-' * 70 + "\n")
        scr.addstr("RPC Tool\n")
        scr.addstr('-' * 70 + "\n")
        scr.addstr(f"Connection url: '{self.state.client.address}'\n")

        try:
            jukebox_version = self.state.client.enque('misc', 'get_version')
        except Exception:
            jukebox_version = "unknown"

        scr.addstr(f"Jukebox version: {jukebox_version}\n")
        scr.addstr(f"Pyzmq version: {zmq.pyzmq_version()}; ZMQ version: {zmq.zmq_version()}; "
                  f"has draft API: {zmq.DRAFT_API}\n")
        scr.addstr('-' * 70 + "\n")
        scr.refresh()

    def _show_help(self, scr, topic: str = '') -> None:
        """Display help information for commands"""
        scr.erase()
        self.update_help(scr)
        max_y, max_x = scr.getmaxyx()
        scr.addstr("Available commands:\n\n")

        for key, value in self.state.rpc_help.items():
            if not key.startswith(topic):
                continue

            sign: str = value['signature']
            sign = sign[sign.find('('):]
            func = f"{key}{sign}"
            scr.addstr(f"{func:50}: {value['description']}\n")

            # Handle pagination
            y, x = scr.getyx()
            if y == max_y - 1:
                scr.addstr("--HIT A KEY TO CONTINUE--")
                scr.getch()
                scr.erase()

        scr.addstr("\n")
        scr.refresh()

    def _show_usage(self, scr) -> None:
        """Display usage information and key bindings"""
        scr.addstr("\n\nUsage:\n")
        scr.addstr("  > cmd [arg1] [arg2] [kwarg1=value1]\n")
        scr.addstr("Examples:\n")
        scr.addstr("  > volume.ctrl.set_volume 50\n")
        example = (
            '  > player.ctrl.play_from_reader '
            'content={"albumartist": "Taylor Swift", "album": "Fearless"} '
            'content_type=album\n'
        )
        scr.addstr(example)
        scr.addstr("\nSupported argument formats:\n")
        scr.addstr("  - Simple values (strings, numbers)\n")
        scr.addstr("  - Hexadecimal numbers (0x...)\n")
        scr.addstr("  - JSON objects and arrays for keyword arguments\n")
        scr.addstr("Note: JSON must be valid and properly quoted\n")
        scr.addstr("\n")
        scr.addstr("Use <TAB> for auto-completion of commands!\n")
        scr.addstr("Use <UP>/<DOWN> for command history!\n")
        scr.addstr("\n")
        scr.addstr("Type help <RET>, to get a list of all commands\n")
        scr.addstr("Type usage <RET>, to get this usage help\n")
        scr.addstr("\n")
        scr.addstr("To exit, press Ctrl-D or type 'exit'\n")
        scr.addstr("\n")
        scr.refresh()

    def _get_common_beginning(self, strings: List[str]) -> str:
        """Find common prefix among a list of strings"""
        if not strings:
            return ""

        result = []
        limit = min(len(s) for s in strings)

        for i in range(limit):
            chars = set(s[i] for s in strings)
            if len(chars) == 1:
                result.append(chars.pop())
            else:
                break

        return ''.join(result)

    def _autocomplete(self, msg: str) -> Tuple[str, List[str]]:
        """Handle command autocompletion"""
        matches = [s for s in self.state.candidates if s.startswith(msg)]
        if not matches:
            return msg, matches

        common = self._get_common_beginning(matches)
        return common, matches

    def _is_printable(self, ch: int) -> bool:
        """Check if character is printable"""
        return 32 <= ch <= 127

    def _reprompt(self, scr, msg: str, y: int, x: int) -> None:
        """Redraw prompt and message"""
        scr.move(y, 0)
        scr.clrtoeol()
        scr.addstr(self.state.prompt)
        scr.addstr(msg)
        scr.move(y, x)

    def _get_input(self, scr) -> str:  # noqa: C901
        """Handle user input with history and autocompletion"""
        ch = 0
        msg = ''
        ihist = ''
        hidx = len(self.state.history)

        y, x = scr.getyx()
        self._reprompt(scr, msg, y, len(self.state.prompt) + len(msg))
        scr.refresh()

        while ch != ord(b'\n'):
            try:
                ch = scr.getch()
            except KeyboardInterrupt:
                return 'exit'

            y, x = scr.getyx()
            pos = x - len(self.state.prompt)

            if ch == ord(b'\t'):
                msg, matches = self._autocomplete(msg)
                if len(matches) > 1:
                    scr.addstr('\n')
                    scr.addstr(', '.join(matches))
                    scr.addstr('\n')
                scr.clrtobot()
                self._reprompt(scr, msg, y, len(self.state.prompt) + len(msg))

            elif ch == ord(b'\n'):
                break
            elif ch == 4:  # Ctrl-D
                return 'exit'
            elif ch in (curses.KEY_BACKSPACE, 127):
                if pos > 0:
                    scr.delch(y, x - 1)
                    msg = msg[0:pos - 1] + msg[pos:]
            elif ch == curses.KEY_DC:
                scr.delch(y, x)
                msg = msg[0:pos] + msg[pos + 1:]
            elif ch == curses.KEY_LEFT:
                if pos > 0:
                    scr.move(y, x - 1)
            elif ch == curses.KEY_RIGHT:
                if pos < len(msg):
                    scr.move(y, x + 1)
            elif ch == curses.KEY_HOME:
                scr.move(y, len(self.state.prompt))
            elif ch == curses.KEY_END:
                scr.move(y, len(self.state.prompt) + len(msg))
            elif ch == curses.KEY_UP:
                if hidx == len(self.state.history):
                    ihist = msg
                hidx = max(hidx - 1, 0)
                msg = self.state.history[hidx]
                self._reprompt(scr, msg, y, len(self.state.prompt) + len(msg))
            elif ch == curses.KEY_DOWN:
                hidx = min(hidx + 1, len(self.state.history))
                msg = ihist if hidx == len(self.state.history) else self.state.history[hidx]
                self._reprompt(scr, msg, y, len(self.state.prompt) + len(msg))
            elif self._is_printable(ch):
                msg = msg[0:pos] + curses.ascii.unctrl(ch) + msg[pos:]
                self._reprompt(scr, msg, y, x + 1)

            scr.refresh()

        self.state.history.append(msg)
        return msg


def main():
    """CLI entry point with argument parsing"""
    default_tcp = 5555
    default_ws = 5556
    default_url = f"tcp://localhost:{default_tcp}"

    parser = argparse.ArgumentParser(
        description='The Jukebox RPC command line tool',
        epilog=f'Default connection: {default_url}'
    )

    port_group = parser.add_mutually_exclusive_group()
    port_group.add_argument(
        "-w", "--websocket",
        help=f"Use websocket protocol on PORT [default: {default_ws}]",
        nargs='?', const=default_ws,
        metavar="PORT", default=None
    )
    port_group.add_argument(
        "-t", "--tcp",
        help=f"Use tcp protocol on PORT [default: {default_tcp}]",
        nargs='?', const=default_tcp,
        metavar="PORT", default=None
    )
    port_group.add_argument(
        "-c", "--command",
        help="Send command to Jukebox server",
        default=None
    )

    args = parser.parse_args()

    url = default_url
    if args.websocket is not None:
        url = f"ws://localhost:{args.websocket}"
    elif args.tcp is not None:
        url = f"tcp://localhost:{args.tcp}"

    print(f">>> RPC Client connect on {url}")

    cli = JukeboxCli(url)

    if args.command is not None:
        # Handle single command execution
        cli.execute_command(None, args.command)
    else:
        # Run interactive CLI
        curses.wrapper(cli.run)

    print(">>> RPC Client exited!")


if __name__ == '__main__':
    main()
