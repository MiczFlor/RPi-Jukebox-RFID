import { memo } from 'react';
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

  const command = 'play_single';
  const {
    artist,
    duration,
    file,
    provider,
    title,
  } = song;

  const playSingle = () => {
    request(command, { song_url: file, provider })
  }

  const registerSongToCard = () => (
    registerMusicToCard(command, { song_url: file, provider })
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

export default memo(SongListItem);
