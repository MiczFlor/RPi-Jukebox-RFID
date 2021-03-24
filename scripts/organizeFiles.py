#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sys
import os


musicConf = """CURRENTFILENAME="filename"
ELAPSED="0"
PLAYSTATUS="Stopped"
RESUME="OFF"
SHUFFLE="OFF"
LOOP="OFF"
SINGLE="OFF"
"""

audiobookConf = """CURRENTFILENAME="filename"
ELAPSED="0"
PLAYSTATUS="Stopped"
RESUME="ON"
SHUFFLE="OFF"
LOOP="OFF"
SINGLE="OFF"
"""


def readShortcuts(shortcutsDir):
    result = {}
    for f in os.listdir(shortcutsDir):
        absf = os.path.join(shortcutsDir, f)
        if os.path.isfile(absf):
            val = []
            with open(absf, "r") as fobj:
                for line in fobj:
                    if len(line.strip()) != 0:
                        val.append(line.rstrip())
            result[f] = val
    return result


def readFolders(audioDir, relpath=None, isFirst=True):
    result = {}
    relpath = "" if relpath is None else relpath
    hasAudioFiles = False
    for f in os.listdir(audioDir):
        absf = os.path.join(audioDir, f)
        if os.path.isfile(absf):
            if not isFirst:
                hasAudioFiles = True
        elif os.path.isdir(absf):
            childResult = readFolders(audioDir=absf, relpath=os.path.join(relpath, f), isFirst=False)
            for k, v in childResult.items():
                assert(k not in result)
                result[k] = v
    if hasAudioFiles:
        result[relpath] = os.path.exists(os.path.join(audioDir, "folder.conf"))
    return result


def _deleteBrokenSymlink(shortcutsDir, cardid, d):
    i = input("\ndelete broken symlink [" + cardid + " --> " + str(d) + "]? [y/N]")
    if i == "y":
        print("deleting symlink.")
        os.remove(os.path.join(shortcutsDir, cardid))
    else:
        print("keeping broken symlink.")


def fixBrokenShortcuts(shortcutsDir, shortcuts, audioFolders):
    for cardid, dirs in shortcuts.items():
        if len(dirs) == 0 and cardid != "placeholder":
            _deleteBrokenSymlink(shortcutsDir=shortcutsDir, cardid=cardid, d=None)
        for d in dirs:
            if d not in audioFolders and d != cardid:
                _deleteBrokenSymlink(shortcutsDir=shortcutsDir, cardid=cardid, d=d)

def _writeFolderConf(audioDir, d, content):
    with open(os.path.join(audioDir, d, "folder.conf"), "w") as f:
        f.write(content)


def _askFolderType(audioDir, d):
    i = input("\ntype of " + d + " ? [m]usic/[a]udiobook/[I]gnore: ")
    if i == "m":
        _writeFolderConf(audioDir=audioDir, d=d, content=musicConf)
    elif i == "a":
        _writeFolderConf(audioDir=audioDir, d=d, content=audiobookConf)
    else:
        print("ignoring folder.")


def linkLooseFolders(shortcutsDir, audioDir, shortcuts, audioFolders):
    allShortcutsDirs = []
    print("\n\n=== linking loose folders")
    for cardid, dirs in shortcuts.items():
        allShortcutsDirs.extend(dirs)
    for d, hasFolderConf in audioFolders.items():
        if d not in allShortcutsDirs:
            cardid = input("\ncardid for [" + d + "]: ")
            if len(cardid) == 0:
                print("ok, ignoring this folder.")
            else:
                doit = True
                if cardid in shortcuts:
                    doit = False
                    yn = input("WARNING: cardid already assigned to " + str(shortcuts[cardid]) + ". Override? [y/N] ")
                    if yn == "y":
                        doit = True

                if doit:
                    if not hasFolderConf:
                        _askFolderType(audioDir=audioDir, d=d)
                    with open(os.path.join(shortcutsDir, cardid), "w") as f:
                        f.write(d)
                else:
                    print("skipping.")
    print("done.")


def fixFoldersWithoutFolderConf(audioDir, audioFolders):
    print("\n\n=== Fixing folders with missing folder.conf ...")
    for d, hasFolderConf in audioFolders.items():
        if not hasFolderConf:
            _askFolderType(audioDir=audioDir, d=d)
    print("=== done.")


if __name__ == "__main__":
    baseDir = "/home/pi/RPi-Jukebox-RFID/shared"
    shortcutsDir = os.path.join(baseDir, "shortcuts")
    audioDir = os.path.join(baseDir, "audiofolders")

    shortcuts = readShortcuts(shortcutsDir=shortcutsDir)
    audioFolders = readFolders(audioDir=audioDir)

    linkLooseFolders(shortcutsDir=shortcutsDir, audioDir=audioDir, shortcuts=shortcuts, audioFolders=audioFolders)
    fixBrokenShortcuts(shortcutsDir=shortcutsDir, shortcuts=shortcuts, audioFolders=audioFolders)

    audioFolders2 = readFolders(audioDir=audioDir)
    fixFoldersWithoutFolderConf(audioDir=audioDir, audioFolders=audioFolders2)

