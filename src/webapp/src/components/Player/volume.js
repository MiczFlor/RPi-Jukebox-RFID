import React, { useContext, useEffect, useState } from 'react';

import Grid from '@mui/material/Grid';
import Slider from '@mui/material/Slider';
import VolumeDownIcon from '@mui/icons-material/VolumeDown';
import VolumeMuteIcon from '@mui/icons-material/VolumeMute';
import VolumeOffIcon from '@mui/icons-material/VolumeOff';
import VolumeUpIcon from '@mui/icons-material/VolumeUp';
import { useTheme } from '@mui/material/styles';

import PlayerContext from '../../context/player/context';
import request from '../../utils/request';

const Volume = () => {
  const theme = useTheme();

  const {
    state,
  } = useContext(PlayerContext);

  const { volume } = state.playerstatus || {};

  const [isChangingVolume, setIsChangingVolume] = useState(false);
  const [_volume, setVolume] = useState(0);

  const [volumeMute, setVolumeMute] = useState(false);
  const [volumeMax] = useState(100);
  const [volumeStep] = useState(1);

  const toggleVolumeMute = () => {
    setVolumeMute(!volumeMute);
    request('toggleMuteVolume', { mute_on: !volumeMute });
  };

  const updateVolume = () => {
    request('setVolume', { volume: _volume });
    // Delay the next command to avoid jumping slide control
    setTimeout(() => setIsChangingVolume(false), 500);
  }

  const handleVolumeChange = (event, newVolume) => {
    setIsChangingVolume(true);
    if (newVolume <= volumeMax) {
      setVolume(newVolume);
    }
  }

  useEffect(() => {
    // Only trigger API when not dragging volume bar
    if (!isChangingVolume) {
      setVolume(volume);
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
      <Grid
        item
        onClick={toggleVolumeMute}
        sx={{ marginRight: theme.spacing(2) }}
      >
        {volumeMute && <VolumeOffIcon />}
        {!volumeMute && _volume === 0 && <VolumeMuteIcon />}
        {!volumeMute && _volume > 0 && _volume < 50 && <VolumeDownIcon />}
        {!volumeMute && _volume >= 50 && <VolumeUpIcon />}
      </Grid>
      <Grid item xs>
        <Slider
          aria-labelledby="Volume Slider"
          onChange={handleVolumeChange}
          onChangeCommitted={updateVolume}
          disabled={volumeMute}
          marks={[ { value: volumeMax } ]}
          size="small"
          step={volumeStep}
          value={typeof _volume === 'number' ? _volume : 0}
          valueLabelDisplay="auto"
        />
      </Grid>
    </Grid>
  );
}

export default Volume;