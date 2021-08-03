import React, { useContext, useEffect, useState } from 'react';
import PropTypes from 'prop-types';

import PlayerContext from '../../context/player/context';

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
  const {
    setVolume,
    state,
    toggleMuteVolume,
  } = useContext(PlayerContext);

  const { volume } = state.playerstatus || {};

  const [isChangingVolume, setIsChangingVolume] = useState(false);
  const [_volume, _setVolume] = useState(volume)

  const [volumeMute, setVolumeMute] = useState(false);
  const [volumeMax] = useState(75);
  const [volumeStep] = useState(1);

  const toggleVolumeMute = () => {
    setVolumeMute(!volumeMute);
    toggleMuteVolume(!volumeMute)
  };

  const updateVolume = () => {
    setVolume(_volume);
    // Delay the next command to avoid jumping slide control
    setTimeout(() => setIsChangingVolume(false), 500);
  }

  const handleVolumeChange = (event, newVolume) => {
    setIsChangingVolume(true);
    if (newVolume <= volumeMax) {
      _setVolume(newVolume);
    }
  }

  useEffect(() => {
    // Only trigger API when not dragging volume bar
    if (!isChangingVolume) {
      _setVolume(volume);
    }
  }, [isChangingVolume, volume]);

  return (
    <Grid container direction="row" justify="center" alignItems="center" className={classes.volume}>
      <Grid item onClick={toggleVolumeMute}>
        {volumeMute && <VolumeOffIcon />}
        {!volumeMute && _volume === 0 && <VolumeMuteIcon />}
        {!volumeMute && _volume > 0 && _volume < 50 && <VolumeDownIcon />}
        {!volumeMute && _volume >= 50 && <VolumeUpIcon />}
      </Grid>
      <Grid item xs>
        <Slider
          ValueLabelComponent={VolumeLabel}
          value={_volume || 0}
          onChange={handleVolumeChange}
          onChangeCommitted={updateVolume}
          disabled={volumeMute}
          marks={[ { value: volumeMax } ]}
          step={volumeStep}
          aria-labelledby="volume slider"
        />
      </Grid>
    </Grid>
  );
}

export default Volume;