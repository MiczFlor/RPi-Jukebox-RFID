import React, { useContext } from 'react';
import { useTranslation } from 'react-i18next';

import PubSubContext from '../../context/pubsub/context';

import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';

const Display = () => {
  const { t } = useTranslation();
  const { state: { player_status } } = useContext(PubSubContext);

  const dontBreak = {
    whiteSpace: 'nowrap',
    width: '100%',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
  };

  return (
    <Grid container>
      <Typography sx={dontBreak} component="h5" variant="h5">
        {player_status.trackid
          ? (player_status.title || t('player.display.unknown-title'))
          : t('player.display.no-song-in-queue')
        }
      </Typography>
      <Typography sx={dontBreak} variant="subtitle1" color="textSecondary">
        {player_status.trackid && (player_status.artist || t('player.display.unknown-artist')) }
        <span> &bull; </span>
        {player_status.trackid && (player_status.album || player_status.file) }
      </Typography>
    </Grid>
  );
};

export default Display;
