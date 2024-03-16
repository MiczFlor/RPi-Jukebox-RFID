import React, { memo } from 'react';
import { dropLast } from "ramda";
import { useTranslation } from 'react-i18next';

import {
  List,
  ListItem,
  Typography,
} from '@mui/material';

import FolderListItem from './folder-list-item';
import FolderListItemBack from './folder-list-item-back';

import { ROOT_DIR } from '../../../../config';

const FolderList = ({
  dir,
  folders,
  isSelecting,
  registerMusicToCard,
}) => {
  const { t } = useTranslation();

  const getParentDir = (dir) => {
    const decodedDir = decodeURIComponent(dir);

    if (decodedDir === ROOT_DIR) return undefined;

    const parentDir = dropLast(1, decodedDir.split('/')).join('/') || ROOT_DIR;
    return parentDir;
  }

  const parentDir = getParentDir(dir);

  return (
    <List sx={{ width: '100%' }}>
      {parentDir &&
        <FolderListItemBack dir={parentDir} />
      }
      {folders.length === 0 &&
        <ListItem sx={{ justifyContent: 'center' }}>
          <Typography>{t('library.folders.empty-folder')}</Typography>
        </ListItem>
      }
      {folders.length > 0 && folders.map((folder, key) =>
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
