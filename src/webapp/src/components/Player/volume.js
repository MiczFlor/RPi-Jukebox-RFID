import React, { useContext, useEffect, useState } from 'react';

import Grid from '@mui/material/Grid';
import Slider from '@mui/material/Slider';
import VolumeDownIcon from '@mui/icons-material/VolumeDown';
import VolumeMuteIcon from '@mui/icons-material/VolumeMute';
import VolumeOffIcon from '@mui/icons-material/VolumeOff';
import VolumeUpIcon from '@mui/icons-material/VolumeUp';

import PlayerContext from '../../context/player/context';

const Volume = () => {
  const {
    setVolume,
    state,
    toggleMuteVolume,
  } = useContext(PlayerContext);

  const { volume } = state.playerstatus || {};

  const [isChangingVolume, setIsChangingVolume] = useState(false);
  const [_volume, _setVolume] = useState(0);

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
    <Grid
      alignItems="center"
      container
      direction="row"
      justifyContent="center"
      sx={{ width: '100%' }}
    >
      <Grid item onClick={toggleVolumeMute}>
        {volumeMute && <VolumeOffIcon />}
        {!volumeMute && _volume === 0 && <VolumeMuteIcon />}
        {!volumeMute && _volume > 0 && _volume < 50 && <VolumeDownIcon />}
        {!volumeMute && _volume >= 50 && <VolumeUpIcon />}
      </Grid>
      <Grid item xs>
        <Slider
          valueLabelDisplay="auto"
          value={typeof _volume === 'number' ? _volume : 0}
          onChange={handleVolumeChange}
          onChangeCommitted={updateVolume}
          disabled={volumeMute}
          marks={[ { value: volumeMax } ]}
          step={volumeStep}
          aria-labelledby="Volume Slider"
        />
      </Grid>
    </Grid>
  );
}

export default Volume;