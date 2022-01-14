import React, { useContext, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import Grid from '@mui/material/Grid';
import IconButton from '@mui/material/IconButton';
import Slider from '@mui/material/Slider';
import VolumeDownIcon from '@mui/icons-material/VolumeDown';
import VolumeMuteIcon from '@mui/icons-material/VolumeMute';
import VolumeOffIcon from '@mui/icons-material/VolumeOff';
import VolumeUpIcon from '@mui/icons-material/VolumeUp';
import { useTheme } from '@mui/material/styles';

import PubSubContext from '../../context/pubsub/context';
import request from '../../utils/request';

const Volume = () => {
  const theme = useTheme();
  const { t } = useTranslation();
  const { state } = useContext(PubSubContext);
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
    const fetchVolume = async () =>  {
      const { result } = await request('getVolume');
      setVolume(result);
    }

    const fetchMaxVolume = async () =>  {
      const { result } = await request('getMaxVolume');
      setMaxVolume(result);
    }

    fetchVolume();
    fetchMaxVolume();
  }, []);

  const labelIcon = () => (
    volumeMute
      ? t('player.volume.unmute')
      : t('player.volume.mute')
  );

  return (
    <Grid
      alignItems="center"
      container
      sx={{ width: '100%' }}
    >
      <Grid item sx={{ marginRight: theme.spacing(1) }}>
        <IconButton
          aria-label={labelIcon()}
          onClick={toggleVolumeMute}
          title={labelIcon()}
        >
          {volumeMute && <VolumeOffIcon />}
          {!volumeMute && _volume === 0 && <VolumeMuteIcon />}
          {!volumeMute && _volume > 0 && _volume < 50 && <VolumeDownIcon />}
          {!volumeMute && _volume >= 50 && <VolumeUpIcon />}
        </IconButton>
      </Grid>
      <Grid item xs sx={{ marginTop: theme.spacing(1) }}>
        <Slider
          aria-labelledby={t('player.volume.slider')}
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