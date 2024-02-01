#!/usr/bin/env python
"""
Command Line Interface to the Jukebox RPC Server

A command line tool for sending RPC commands to the running jukebox app.
This uses the same interface as the WebUI. Can be used for additional control
or for debugging.

The tool features auto-completion and command history.

The list of available commands is fetched from the running Jukebox service.

.. todo:
   - kwargs support

"""

import argparse
import zmq
import curses
import curses.ascii
import jukebox.rpc.client as rpc

# Developers note: Scripting at it's dirty end :-)


# Careful: curses and default outputs don't mix!
# In case you'll get an error, most likely your terminal may become funny
# Best bet: Just don't configure any logger at all!
# import logging
# import misc.loggingext
# logger = misc.loggingext.configure_default(logging.ERROR)


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
        # print(f"{func:50}: {value['description']}")
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
    scr.addstr("  > volume.ctrl.set_volume 50\n")
    scr.addstr("Note: NOT yet supported: kwargs, quoting!\n")
    scr.addstr("\n")
    scr.addstr("Numbers are supported in decimal and hexadecimal format when prefixed with '0x'")
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
    # logger.debug(f"Autocomplete {msg}")
    # Get all stings that match the beginning
    # candidates = ["ap1", 'ap2', 'appbbb3', 'appbbb4', 'appbbb5', 'appbbb6', 'exit']
    matches = [s for s in candidates if s.startswith(msg)]
    if len(matches) == 0:
        # Matches is empty: nothing found
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


def get_input(scr):  # noqa: C901
    curses.noecho()
    ch = 0
    msg = ''
    ihist = ''
    hidx = len(history)
    [y, x] = scr.getyx()
    reprompt(scr, msg, y, len(prompt) + len(msg))
    scr.refresh()
    while ch != ord(b'\n'):
        try:
            ch = scr.getch()
        except KeyboardInterrupt:
            msg = 'exit'
            break
        [y, x] = scr.getyx()
        pos = x - len(prompt)
        if ch == ord(b'\t'):
            msg, matches = autocomplete(msg)
            if len(matches) > 1:
                scr.addstr('\n')
                scr.addstr(', '.join(matches))
                scr.addstr('\n')
            scr.clrtobot()
            reprompt(scr, msg, y, len(prompt) + len(msg))
        if ch == ord(b'\n'):
            break
        if ch == 4:
            msg = 'exit'
            break
        elif ch == curses.KEY_BACKSPACE or ch == 127:
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
            scr.move(y, len(prompt))
        elif ch == curses.KEY_END:
            scr.move(y, len(prompt) + len(msg))
        elif ch == curses.KEY_UP:
            if hidx == len(history):
                ihist = msg
            hidx = max(hidx - 1, 0)
            msg = history[hidx]
            reprompt(scr, msg, y, len(prompt) + len(msg))
        elif ch == curses.KEY_DOWN:
            hidx = min(hidx + 1, len(history))
            if hidx == len(history):
                msg = ihist
            else:
                msg = history[hidx]
            reprompt(scr, msg, y, len(prompt) + len(msg))
        elif is_printable(ch):
            msg = msg[0:pos] + curses.ascii.unctrl(ch) + msg[pos:]
            reprompt(scr, msg, y, x + 1)
        # else:
        #     print(f" {ch} -- {type(ch)}")
        scr.refresh()
    scr.refresh()
    history.append(msg)
    return msg


def tonum(string_value):
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
        # Split on whitespaces to separate cmd and arg list
        dec = [v for v in cmd.strip().split(' ') if len(v) > 0]
        if len(dec) == 0:
            continue
        elif dec[0] == 'help':
            topic = ''
            if len(dec) > 1:
                topic = dec[1]
            format_help(scr, topic)
            continue
        elif dec[0] == 'usage':
            format_usage(scr)
            continue
        # scr.addstr(f"\n{cmd}\n")
        # Split cmd on '.' into package.plugin.method
        # Remove duplicate '.' along the way
        sl = [v for v in dec[0].split('.') if len(v) > 0]
        fargs = [tonum(a) for a in dec[1:]]
        scr.addstr(f"\n:: Command = {sl}, args = {fargs}\n")
        response = None
        method = None
        if not (2 <= len(sl) <= 3):
            scr.addstr(":: Error = Ill-formatted command\n")
            continue
        if len(sl) == 3:
            method = sl[2]
        try:
            response = client.enque(sl[0], sl[1], method, args=fargs)
        except zmq.error.Again:
            scr.addstr("\n\n" + '-' * 70 + "\n")
            scr.addstr("Could not reach RPC Server. Jukebox running? Correct Port?\n")
            scr.addstr('-' * 70 + "\n\n")
            scr.refresh()
        except Exception as e:
            scr.addstr(f":: Exception response =\n{e}\n")
        else:
            scr.addstr(f"\n:: Response =\n{response}\n\n")


def runcmd(cmd):
    """
    Just run a command.
    Right now duplicates more or less main()
    :todo remove duplication of code
    """

    # Split on whitespaces to separate cmd and arg list
    dec = [v for v in cmd.strip().split(' ') if len(v) > 0]
    if len(dec) == 0:
        return
    # Split cmd on '.' into package.plugin.method
    # Remove duplicate '.' along the way
    sl = [v for v in dec[0].split('.') if len(v) > 0]
    fargs = [tonum(a) for a in dec[1:]]
    response = None
    method = None
    if not (2 <= len(sl) <= 3):
        print(":: Error = Ill-formatted command\n")
        return
    if len(sl) == 3:
        method = sl[2]
    try:
        response = client.enque(sl[0], sl[1], method, args=fargs)
    except zmq.error.Again:
        print("\n\n" + '-' * 70 + "\n")
        print("Could not reach RPC Server. Jukebox running? Correct Port?\n")
        print('-' * 70 + "\n\n")
        return
    except Exception as e:
        print(f":: Exception response =\n{e}\n")
        return
    else:
        print(f"\n:: Response =\n{response}\n\n")


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
