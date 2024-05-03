#!/usr/bin/env python
"""
A command line tool that monitors all messages being sent out from the
Jukebox via the publishing interface.  Received messages are printed in the console.
Mainly used for debugging.
"""
import argparse
import logging
import misc.loggingext
from jukebox.publishing.subscriber import Subscriber

logger = misc.loggingext.configure_default(logging.WARNING)
topic_width = 40


def main(address, topic):
    sub = Subscriber(address, topic)
    while True:
        try:
            [topic, payload] = sub.receive()
        except KeyboardInterrupt:
            break
        print(f"{topic:{topic_width}}: {payload}")


if __name__ == '__main__':
    default_ws = 5557
    default_tcp = 5558
    url = f"tcp://localhost:{default_tcp}"
    argparser = argparse.ArgumentParser(description='The Jukebox Publisher sniffer tool',
                                        epilog=f'Default connection: {url}\nExample:\n$ {__file__} -t 5558 -k core host',
                                        formatter_class=argparse.RawDescriptionHelpFormatter)
    port_group = argparser.add_mutually_exclusive_group()
    port_group.add_argument("-w", "--websocket",
                            help=f"Use websocket protocol on PORT [default: {default_ws}]",
                            nargs='?', const=default_ws,
                            metavar="PORT", default=None)
    port_group.add_argument("-t", "--tcp",
                            help=f"Use tcp protocol on PORT [default: {default_tcp}]",
                            nargs='?', const=default_tcp,
                            metavar="PORT", default=None)

    argparser.add_argument('-k', '--topics', metavar='TOPIC',
                           help="Subscribe to this topic tree(s). If omitted all topics are subscribed.",
                           nargs='+',
                           default='')
    args = argparser.parse_args()

    if args.websocket is not None:
        url = f"ws://localhost:{args.websocket}"
    elif args.tcp is not None:
        url = f"tcp://localhost:{args.tcp}"

    print(f">>> Sniffer Client connect on {url} for topics '{args.topics}'\n\n")

    main(url, args.topics)

    print("\n\n>>> Sniffer Client exited!")
