import React from 'react';
import { useTranslation } from 'react-i18next';

import {
  Grid,
  Typography,
} from '@mui/material';

import SelectCommandAliases from './select-command-aliases';
import SelectPlayMusic from './actions/play-music';
import SelectTimers from './actions/timers';
import SelectAudio from './actions/audio';
import { buildActionData } from '../utils';
import SelectHost from './actions/host';

const ControlsSelector = ({
  actionData,
  setActionData,
  cardId,
}) => {
  const { t } = useTranslation();

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
          <Typography>
            {t('cards.controls.controls-selector.label')}
          </Typography>
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
        {actionData.action === 'host' &&
          <SelectHost
          actionData={actionData}
          handleActionDataChange={handleActionDataChange}
          />
        }

        {actionData.action === 'play_music' &&
          <SelectPlayMusic
            actionData={actionData}
            cardId={cardId}
          />
        }

        {actionData.action === 'timers' &&
          <SelectTimers
            actionData={actionData}
            handleActionDataChange={handleActionDataChange}
          />
        }

        {actionData.action === 'audio' &&
          <SelectAudio
            actionData={actionData}
            handleActionDataChange={handleActionDataChange}
          />
        }
      </Grid>
    </Grid>
  );
};

export default ControlsSelector;