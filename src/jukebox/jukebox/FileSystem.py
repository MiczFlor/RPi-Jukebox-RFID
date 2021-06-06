#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import logging

logger = logging.getLogger('jb.filesystem')

class filesystem_control:
    def __init__(self, audiofolder_path):
        self.audiofolder_path = audiofolder_path

    def get_all_folders_flattened(self):
        folders_raw = [x[0] for x in os.walk(self.audiofolder_path)]
        folders = []

        for path in folders_raw:
            label = path.replace(self.audiofolder_path + "/", "")

            if (label == self.audiofolder_path):
                label = "root"

            folder_object = { 'path': path, 'label': label }
            folders.append(folder_object)

        return ({'object': 'filesystem', 'method': 'get_all_folders_flattened', 'params': { 'folders': folders }})
