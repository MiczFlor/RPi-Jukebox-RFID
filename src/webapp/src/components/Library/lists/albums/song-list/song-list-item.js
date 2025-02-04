import React from 'react';
import { useTranslation } from 'react-i18next';

import {
  ListItem,
  ListItemButton,
  ListItemText,
} from '@mui/material';

import { toHHMMSS } from '../../../../../utils/utils';
import request from '../../../../../utils/request'

const SongListItem = ({
  isSelecting,
  registerContentToCard,
  song,
}) => {
  const { t } = useTranslation();

  const {
    artist,
    duration,
    file,
    title,
  } = song;

  const playSingle = () => {
    request('play_content', { content: file, content_type: 'single' })
  }

  const registerSingleToCard = () => (
    registerContentToCard('play_content', { content: file, content_type: 'single' })
  );

  return (
    <ListItem disablePadding>
      <ListItemButton
        role={undefined}
        onClick={() => (isSelecting ? registerSingleToCard() : playSingle())}
      >
        <ListItemText
          primary={title || t('library.albums.unknown-title')}
          secondary={`${artist || t('library.albums.unknown-artist')} • ${toHHMMSS(duration)}`}
        />
      </ListItemButton>
    </ListItem>
  );
}

export default React.memo(SongListItem);
