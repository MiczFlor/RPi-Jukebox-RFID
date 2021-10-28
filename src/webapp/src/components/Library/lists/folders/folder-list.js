import React, { memo } from 'react';
import { dropLast } from "ramda";

import { List } from '@mui/material';

import FolderListItem from './folder-list-item';
import FolderListItemBack from './folder-list-item-back';

const FolderList = ({ folders, dir }) => {
  const getParentDir = (dir) => {
    // TODO: ROOTS should be removed after paths are relative
    const ROOTS = ['./', '/home/pi/RPi-Jukebox-RFID/shared/audiofolders'];
    const decodedDir = decodeURIComponent(dir);

    if (ROOTS.includes(decodedDir)) return undefined;

    const parentDir = dropLast(1, decodedDir.split('/')).join('/');
    return parentDir;
  }

  const parentDir = getParentDir(dir);

  return (
    <List sx={{ width: '100%', bgcolor: 'background.paper' }}>
      {parentDir &&
        <FolderListItemBack
          dir={parentDir}
        />
      }
      {folders.map(FolderListItem)}
    </List>
  );
}

export default memo(FolderList);
