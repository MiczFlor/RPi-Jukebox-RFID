import React from 'react';

import {
  Grid,
  Typography
} from '@mui/material';

import SelectPlayCards from './select-play-cards';
import SelectCommandAliases from './select-command-aliases';

const ControlsSelector = ({
  selectedAction,
  setSelectedAction,
  selectedAlbum,
  setSelectedAlbum,
}) => {
  const handleActionChange = (event) => {
    setSelectedAction(event.target.value);
    setSelectedAlbum(undefined);
  };

  const handleAlbumChange = (album) => {
    setSelectedAlbum(album);
  };

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
          <Grid container direction="row" alignItems="center">
            <Grid item xs={5}>
              <Typography>Albums</Typography>
            </Grid>
            <Grid item xs={7}>
              <SelectPlayCards
                selectedAlbum={selectedAlbum}
                handleAlbumChange={handleAlbumChange}
              />
            </Grid>
          </Grid>
        }
      </Grid>
    </Grid>
  );
};

export default ControlsSelector;