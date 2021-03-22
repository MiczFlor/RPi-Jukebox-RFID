#!/usr/bin/env python3

import sys
import readersupport as rs


def usage():
    print(f"Usage: {sys.argv[0]} [debug]")


if __name__ == '__main__':
    rs.logconsole.setLevel(rs.logging.INFO)
    if len(sys.argv) == 2:
        print("Setting logging level to DEBUG.")
        rs.logconsole.setLevel(rs.logging.DEBUG)
    elif len(sys.argv) > 2:
        usage()
        sys.exit()

    rs.write_config('../../settings/rfid_reader.ini', rs.query_user_for_reader())
