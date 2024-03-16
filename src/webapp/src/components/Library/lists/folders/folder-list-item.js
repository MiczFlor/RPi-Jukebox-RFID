import React from 'react';
import { useTranslation } from 'react-i18next';

import {
  IconButton,
  ListItem,
  ListItemButton,
  ListItemText,
} from '@mui/material';

import NavigateNextIcon from '@mui/icons-material/NavigateNext';

import request from '../../../../utils/request';
import FolderLink from './folder-link';
import FolderTypeAvatar from './folder-type-avatar';

const FolderListItem = ({
  folder,
  isSelecting,
  registerMusicToCard,
}) => {
  const { t } = useTranslation();
  const { type, name, relpath } = folder;

  const playItem = () => {
    switch(type) {
      case 'directory': return request('play_folder', { folder: relpath, recursive: true });
      case 'file': return request('play_single', { song_url: relpath });
      // TODO: Add missing Podcast
      // TODO: Add missing Stream
      default: return;
    }
  }

  const registerItemToCard = () => {
    switch(type) {
      case 'directory': return registerMusicToCard('play_folder', { folder: relpath, recursive: true });
      case 'file': return registerMusicToCard('play_single', { song_url: relpath });
      // TODO: Add missing Podcast
      // TODO: Add missing Stream
      default: return;
    }
  }

  return (
    <ListItem
      disablePadding
      secondaryAction={
        type === 'directory'
          ? <IconButton
              component={FolderLink}
              data={{ dir: relpath }}
              edge="end"
              aria-label={t('library.folders.show-folder-content')}
            >
              <NavigateNextIcon />
            </IconButton>
          : undefined
      }
    >
      <ListItemButton onClick={() => (isSelecting ? registerItemToCard() : playItem())}>
        <FolderTypeAvatar type={type} />
        <ListItemText primary={name} />
      </ListItemButton>
    </ListItem>
  );
}

export default FolderListItem;
