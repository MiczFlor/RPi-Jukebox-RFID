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
  const { state } = useContext(PlayerContext);
  const { 'volume.level': { volume, mute } = {} } = state;

  const [isChangingVolume, setIsChangingVolume] = useState(false);
  const [_volume, setVolume] = useState(0);
  const [volumeMute, setVolumeMute] = useState(false);
  const [maxVolume, setMaxVolume] = useState(100);
  const [volumeStep] = useState(1);

  const toggleVolumeMute = () => {
    setVolumeMute(!volumeMute);
    request('toggleMuteVolume', { mute: !volumeMute });
  };

  const updateVolume = () => {
    request('setVolume', { volume: _volume });
    // Delay the next command to avoid jumping slide control
    setTimeout(() => setIsChangingVolume(false), 500);
  }

  const handleVolumeChange = (event, newVolume) => {
    setIsChangingVolume(true);
    if (newVolume <= maxVolume) {
      setVolume(newVolume);
    }
  }

  useEffect(() => {
    // Only trigger API when not dragging volume bar
    if (volume !== undefined && mute !== undefined && !isChangingVolume) {
      setVolume(volume);
      setVolumeMute(!!mute);
    }
  }, [isChangingVolume, volume, mute]);

  useEffect(() => {
    const fetchMaxVolume = async () =>  {
      const { result } = await request('getMaxVolume');
      setMaxVolume(result);
    }

    fetchMaxVolume();
  }, []);

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
          disabled={!!volumeMute}
          marks={[ { value: maxVolume } ]}
          step={volumeStep}
          value={_volume}
          valueLabelDisplay="auto"
        />
      </Grid>
    </Grid>
  );
}

export default Volume;