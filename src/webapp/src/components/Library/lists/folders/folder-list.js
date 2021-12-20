import React, { memo } from 'react';
import { dropLast } from "ramda";

import { List } from '@mui/material';

import FolderListItem from './folder-list-item';
import FolderListItemBack from './folder-list-item-back';

import { ROOT_DIRS } from '../../../../config';

const FolderList = ({
  dir,
  folders,
  isSelecting,
  registerMusicToCard,
}) => {
  const getParentDir = (dir) => {
    // TODO: ROOT_DIRS should be removed after paths are relative
    const decodedDir = decodeURIComponent(dir);

    if (ROOT_DIRS.includes(decodedDir)) return undefined;

    const parentDir = dropLast(1, decodedDir.split('/')).join('/');
    return parentDir;
  }

  const parentDir = getParentDir(dir);

  return (
    <List sx={{ width: '100%' }}>
      {parentDir &&
        <FolderListItemBack
          dir={parentDir}
        />
      }
      {folders.map((folder, key) =>
        <FolderListItem
          key={key}
          folder={folder}
          isSelecting={isSelecting}
          registerMusicToCard={registerMusicToCard}
        />
      )}
    </List>
  );
}

export default memo(FolderList);
