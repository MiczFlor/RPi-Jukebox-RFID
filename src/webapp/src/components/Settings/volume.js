import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import {
  Card,
  CardContent,
  CardHeader,
  Divider,
  Grid,
  Slider,
  Typography,
} from '@mui/material';
import { useTheme } from '@mui/material/styles';

import request from '../../utils/request';

const marks = [5, 25, 50, 75, 100].map(
  (value) => ({ value, label: `${value}%` })
);

const SettingsVolume = () => {
  const { t } = useTranslation();
  const theme = useTheme();

  const [maxVolume, setMaxVolume] = useState(0);

  const updateMaxVolume = () => {
    (async () => {
      await request('setMaxVolume', { max_volume: maxVolume });
    })();
  }

  const handleMaxVolumeChange = (event, newMaxVolume) => {
    setMaxVolume(newMaxVolume);
  }

  useEffect(() => {
    const fetchMaxVolume = async () =>  {
      const { result } = await request('getMaxVolume');
      setMaxVolume(result);
    }

    fetchMaxVolume();
  }, []);

  return (
    <Card>
      <CardHeader title={t('settings.volume.title')} />
      <Divider />
      <CardContent>
        <Grid container direction="column">
          <Typography>{t('settings.volume.max-volume')}</Typography>
          <Grid item sx={{ padding: theme.spacing(1) }}>
            <Slider
              value={typeof maxVolume === 'number' ? maxVolume : 0}
              onChange={handleMaxVolumeChange}
              onChangeCommitted={updateMaxVolume}
              marks={marks}
              max={100}
              min={0}
              step={5}
              valueLabelDisplay="auto"
            />
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};

export default SettingsVolume;
