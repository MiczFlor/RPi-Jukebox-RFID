import React from 'react';

import {
  ListItem,
  ListItemButton,
  ListItemText,
} from '@mui/material';

import { LABELS } from '../../../config';
import { toHHMMSS } from '../../../utils/utils';
import request from '../../../utils/request';

const SongListItem = ({ song }) => {
  const {
    artist,
    duration,
    file,
    title,
  } = song;

  return (
    <ListItem disablePadding>
      <ListItemButton
        role={undefined}
        onClick={e => request('playSong', { song_url: file })}
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
