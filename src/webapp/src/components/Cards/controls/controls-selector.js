import React from 'react';

import {
  Grid,
  Typography,
} from '@mui/material';

import SelectPlayCards from './select-play-cards';
import SelectCommandAliases from './select-command-aliases';
import SliderChangeVolume from './slider-change-volume';

const ControlsSelector = ({
  selectedAction,
  setSelectedAction,
  actionData,
  setActionData,
}) => {
  const handleActionChange = (event) => {
    setSelectedAction(event.target.value);
    setActionData({});
  };

  const handleActionDataChange = (action, values) => {
    setActionData({ [action]: values });
  }

  return (
    <Grid container direction="column">
      <Grid container direction="row" alignItems="center">
        <Grid item xs={5}>
          <Typography>Jukebox action</Typography>
        </Grid>
        <Grid item xs={7}>
          <SelectCommandAliases
            selectedAction={selectedAction}
            handleActionChange={handleActionChange}
          />
        </Grid>

        {/* Albums */}
        {selectedAction === 'play_album' &&
          <SelectPlayCards
            actionData={actionData}
            handleActionDataChange={handleActionDataChange}
          />
        }
        {selectedAction === 'change_volume' &&
          <SliderChangeVolume
            actionData={actionData}
            handleActionDataChange={handleActionDataChange}
          />
        }
      </Grid>
    </Grid>
  );
};

export default ControlsSelector;