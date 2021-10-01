import React from 'react';

import {
  Grid,
  Typography
} from '@mui/material';

import SelectPlayCards from './select-play-cards';
import SelectQuickSelects from './select-quick-selects';

const ControlsSelector = ({
  selectedAction,
  setSelectedAction,
  selectedFolder,
  setSelectedFolder,
}) => {
  const handleActionChange = (event) => {
    setSelectedAction(event.target.value);
    setSelectedFolder(undefined);
  };

  const handleFolderChange = (event) => {
    setSelectedFolder(event.target.value);
  };

  return (
    <Grid container direction="column">
      <Grid container direction="row" alignItems="center">
        <Grid item xs={5}>
          <Typography>Jukebox action</Typography>
        </Grid>
        <Grid item xs={7}>
          <SelectQuickSelects
            selectedAction={selectedAction}
            handleActionChange={handleActionChange}
          />
        </Grid>

        {/* Folders */}
        {selectedAction === 'play_card' &&
          <Grid container direction="row" alignItems="center">
            <Grid item xs={5}>
              <Typography>Folders</Typography>
            </Grid>
            <Grid item xs={7}>
              <SelectPlayCards
                selectedFolder={selectedFolder}
                handleFolderChange={handleFolderChange}
              />
            </Grid>
          </Grid>
        }
      </Grid>
    </Grid>
  );
};

export default ControlsSelector;