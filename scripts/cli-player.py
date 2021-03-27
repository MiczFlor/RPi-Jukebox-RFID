#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import subprocess
from organizeFiles import readFolders


if __name__ == "__main__":
    baseDir = "/home/pi/RPi-Jukebox-RFID"
    shortcutsDir = os.path.join(baseDir, "shared", "shortcuts")
    audioDir = os.path.join(baseDir, "shared", "audiofolders")
    scriptsDir = os.path.join(baseDir, "scripts")

    print("=== audio folders:")
    audioFolders = {}
    folders = readFolders(audioDir=audioDir)
    lc2 = 0
    for d2, hasFolderConf2 in sorted(folders.items()):
        print(str(lc2) + ": " + d2)
        audioFolders[lc2] = d2
        lc2 = lc2 + 1

    while True:
        i = input("select folder: ")
        if len(i.strip()) == 0:
            break
        if not i.isnumeric():
            print("not a number.")
            continue
        inum = int(i)
        if inum not in audioFolders:
            print("invalid option")
            continue
        selectedFolder = audioFolders[inum]
        print("  playing " + selectedFolder)
        subprocess.check_output([scriptsDir + '/rfid_trigger_play.sh', '--dir=' + selectedFolder], shell=False)

    print("bye.")

