import React from 'react';

import {
  ListItem,
  ListItemButton,
  ListItemText,
} from '@mui/material';

import { LABELS } from '../../../../../config';
import { toHHMMSS } from '../../../../../utils/utils';
import request from '../../../../../utils/request'

const SongListItem = ({
  isSelecting,
  registerMusicToCard,
  song,
}) => {
  const command = 'play_single';

  const {
    artist,
    duration,
    file,
    title,
  } = song;

  const playSingle = () => {
    request(command, { song_url: file })
  }

  const registerSongToCard = () => (
    registerMusicToCard(command, { song_url: file })
  );

  return (
    <ListItem disablePadding>
      <ListItemButton
        role={undefined}
        onClick={() => (isSelecting ? registerSongToCard() : playSingle())}
      >
        <ListItemText
          primary={title || LABELS.UNKNOW_TITLE}
          secondary={`${artist || LABELS.UNKNOW_ARTIST} • ${toHHMMSS(duration)}`}
        />
      </ListItemButton>
    </ListItem>
  );
}

export default React.memo(SongListItem);
