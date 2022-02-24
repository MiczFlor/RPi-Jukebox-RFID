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
  registerMusicToCard,
  song,
}) => {
  const { t } = useTranslation();

  const command = 'mpd.play_uri';
  const {
    artist,
    duration,
    file,
    title,
  } = song;

  const uri = `mpd:file:${file}`;

  const playSingle = () => (
    request(command, { uri })
  );

  const registerSongToCard = () => (
    registerMusicToCard(command, { uri })
  );

  return (
    <ListItem disablePadding>
      <ListItemButton
        role={undefined}
        onClick={() => (isSelecting ? registerSongToCard() : playSingle())}
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
