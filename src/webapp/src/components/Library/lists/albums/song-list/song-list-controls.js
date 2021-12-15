import React from 'react';

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
  const command = 'play_album';

  const playAlbum = () => (
    request(command, { albumartist, album })
  );

  const registerAlbumToCard = () => (
    registerMusicToCard(command, { albumartist, album })
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
              >
                Assign album to card
              </Button>
        }
      </Grid>
    </Grid>
  );
};

export default SongListControls;
