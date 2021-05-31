import React from 'react';
import PropTypes from 'prop-types';

import { makeStyles } from '@material-ui/core/styles';
import Grid from '@material-ui/core/Grid';
import Slider from '@material-ui/core/Slider';
import Tooltip from '@material-ui/core/Tooltip';
import VolumeDownIcon from '@material-ui/icons/VolumeDown';
import VolumeMuteIcon from '@material-ui/icons/VolumeMute';
import VolumeOffIcon from '@material-ui/icons/VolumeOff';
import VolumeUpIcon from '@material-ui/icons/VolumeUp';

const useStyles = makeStyles({
  volume: {
    width: '100%',
  },
});

function VolumeLabel(props) {
  const { children, open, value } = props;

  return (
    <Tooltip
      open={open}
      enterTouchDelay={100}
      placement="top"
      title={value}>
      {children}
    </Tooltip>
  );
}

VolumeLabel.propTypes = {
  children: PropTypes.element.isRequired,
  open: PropTypes.bool.isRequired,
  value: PropTypes.number.isRequired,
};

const Volume = () => {
  const classes = useStyles();
  const [volumeOff, setVolumeOff] = React.useState(false);
  const [volumeMax, setVolumeMax] = React.useState(75);

  const [volume, setVolume] = React.useState(30);

  const toggleVolumeOff = () => {
    setVolumeOff(!volumeOff);
  };

  const updateVolume = (event, newVolume) => {
    if (newVolume <= volumeMax) {
      setVolume(newVolume);
    }
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
            ValueLabelComponent={VolumeLabel}
            value={volume}
            onChange={updateVolume}
            disabled={volumeOff}
            marks={[ { value: volumeMax } ]}
            aria-labelledby="volume slider"
          />
        </Grid>
      </Grid>
    </div>
  );
}

export default Volume;