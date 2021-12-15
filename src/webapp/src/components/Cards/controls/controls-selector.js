import React from 'react';

import {
  Grid,
  Typography,
} from '@mui/material';

import SelectCommandAliases from './select-command-aliases';
import SelectPlayMusic from './actions/play-music';
import SelectVolume from './actions/volume';
import { buildActionData } from '../utils';

const ControlsSelector = ({
  actionData,
  setActionData,
  cardId,
}) => {
  const handleActionChange = (event) => {
    setActionData(
      buildActionData(event.target.value)
    );
  };

  const handleActionDataChange = (action, command, args) => {
    setActionData(
      buildActionData(action, command, args)
    );
  }

  return (
    <Grid container direction="column">
      <Grid container direction="row" alignItems="center">
        <Grid item xs={5}>
          <Typography>Jukebox action</Typography>
        </Grid>
        <Grid item xs={7}>
          <SelectCommandAliases
            actionData={actionData}
            handleActionChange={handleActionChange}
          />
        </Grid>
      </Grid>
      <Grid
        container
        direction="row"
        alignItems="center"
        sx={{ marginTop: '20px' }}
      >
        {actionData.action === 'play_music' &&
          <SelectPlayMusic
            actionData={actionData}
            cardId={cardId}
          />
        }
        {actionData.action === 'volume' &&
          <SelectVolume
            actionData={actionData}
            handleActionDataChange={handleActionDataChange}
          />
        }

        {actionData.action === 'host' &&
          <Typography>Host</Typography>
        }
      </Grid>
    </Grid>
  );
};

export default ControlsSelector;