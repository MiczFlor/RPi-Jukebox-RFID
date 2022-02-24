import React, { memo } from 'react';
import { dropLast } from "ramda";

import { List } from '@mui/material';

import FolderListItem from './folder-list-item';
import FolderListItemBack from './folder-list-item-back';

import { ROOT_DIRS } from '../../../../config';

const FolderList = ({
  path,
  folders,
  isSelecting,
  registerMusicToCard,
}) => {
  const getParent = (path) => {
    const decodedPath = decodeURIComponent(path);

    // TODO: ROOT_DIRS should be removed after paths are relative
    if (ROOT_DIRS.includes(decodedPath)) return undefined;

    return dropLast(1, decodedPath.split('/')).join('/') || './';
  }

  const parent = getParent(path);

  return (
    <List sx={{ width: '100%' }}>
      {parent &&
        <FolderListItemBack
          path={parent}
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
