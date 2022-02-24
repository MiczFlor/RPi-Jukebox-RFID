import React from 'react';
import { useTranslation } from 'react-i18next';

import {
  Button,
  Grid,
  IconButton,
} from '@mui/material';

import PlayCircleFilledRoundedIcon from '@mui/icons-material/PlayCircleFilledRounded';
import request from '../../../../../utils/request';

const SongListControls = ({
  albumartist,
  album,
  disabled,
  registerMusicToCard,
  isSelecting
}) => {
  const { t } = useTranslation();

  const command = 'mpd.play_uri';
  const uri = [
    'mpd',
    'album', encodeURI(album),
    'albumartist', encodeURI(albumartist)
  ].join(':');

  const playAlbum = () => (
    request(command, { uri })
  );

  const registerAlbumToCard = () => (
    registerMusicToCard(command, { uri })
  );

  return (
    <Grid container sx={{ padding: '0 8px' }}>
      <Grid item xs={12}
        sx={{
          display: 'flex',
          justifyContent: 'right',
        }}
      >
        {
          !isSelecting
            ? <IconButton
                aria-label="Play"
                onClick={playAlbum}
                disabled={disabled}
                size="large"
              >
                <PlayCircleFilledRoundedIcon color="primary" style={{ fontSize: 64 }} />
              </IconButton>
            : <Button
                variant="outlined"
                onClick={registerAlbumToCard}
                sx={{ margin: '20px 0 4px' }}
              >
                {t('library.albums.assign-to-card')}
              </Button>
        }
      </Grid>
    </Grid>
  );
};

export default SongListControls;
