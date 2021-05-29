import React from 'react';

import { makeStyles } from '@material-ui/core/styles';
import Grid from '@material-ui/core/Grid';
import Slider from '@material-ui/core/Slider';
import VolumeDownIcon from '@material-ui/icons/VolumeDown';
import VolumeMuteIcon from '@material-ui/icons/VolumeMute';
import VolumeOffIcon from '@material-ui/icons/VolumeOff';
import VolumeUpIcon from '@material-ui/icons/VolumeUp';

const useStyles = makeStyles({
  volume: {
    width: '100%',
  },
});

const Volume = () => {
  const classes = useStyles();
  const [volumeOff, setVolumeOff] = React.useState(false);
  const [volume, setVolume] = React.useState(30);

  const toggleVolumeOff = () => {
    setVolumeOff(!volumeOff);
  };

  const updateVolume = (event, newVolume) => {
    setVolume(newVolume);
  }

  return (
    <div className={classes.volume}>
      <Grid container spacing={2} direction="row" justify="center" alignItems="center">
        <Grid item onClick={toggleVolumeOff}>
          {volumeOff && <VolumeOffIcon />}
          {!volumeOff && volume === 0 && <VolumeMuteIcon />}
          {!volumeOff && volume > 0 && volume < 50 && <VolumeDownIcon />}
          {!volumeOff && volume >= 50 && <VolumeUpIcon />}
        </Grid>
        <Grid item xs>
          <Slider
            value={volume}
            onChange={updateVolume}
            disabled={volumeOff}
            aria-labelledby="continuous-slider"
          />
        </Grid>
      </Grid>
    </div>
  );
}

export default Volume;