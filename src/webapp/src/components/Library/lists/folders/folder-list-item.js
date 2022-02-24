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
import { DEFAULT_AUDIO_DIR } from '../../../../config';

const FolderListItem = ({
  folder,
  isSelecting,
  registerMusicToCard,
}) => {
  const { t } = useTranslation();
  const { directory, file } = folder;
  const type = directory ? 'directory' : 'file';
  const path = directory || file;
  const name = directory || folder.title;

  const playItem = () => {
    switch(type) {
      case 'directory': return request('mpd.play_uri', { uri: `mpd:folder:${path}` });
      case 'file': return request('mpd.play_uri', { uri: `mpd:file:${path}` });
      // TODO: Add missing Podcast
      // TODO: Add missing Stream
      default: return;
    }
  }

  const registerItemToCard = () => {
    switch(type) {
      case 'directory': return registerMusicToCard('mpd.play_uri', { uri: `mpd:folder:${path}` });
      case 'file': return registerMusicToCard('mpd.play_uri', { uri: `mpd:file:${path}` });
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
              data={{ path }}
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
