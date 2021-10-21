import React, { useEffect, useState } from 'react';

import {
  Card,
  CardContent,
  CardHeader,
  Divider,
  Grid,
  Slider,
  Typography,
} from '@mui/material';

import {
  getMaxVolume,
  setMaxVolume
} from '../../utils/requests';

const marks = [5, 25, 50, 75, 100].map(
  (value) => ({ value, label: `${value}%` })
);

const SettingsVolume = () => {
  const [volumeStep] = useState(5);
  const [_maxVolume, _setMaxVolume] = useState(0);

  const updateMaxVolume = () => {
    (async () => {
      await setMaxVolume(_maxVolume);
    })();
  }

  const handleMaxVolumeChange = (event, newMaxVolume) => {
    _setMaxVolume(newMaxVolume);
  }

  useEffect(() => {
    const fetchMaxVolume = async () =>  {
      const { result } = await getMaxVolume();
      _setMaxVolume(result);
    }

    fetchMaxVolume();
  }, []);

  return (
    <Card>
      <CardHeader title="Volume" />
      <Divider />
      <CardContent>
        <Grid container direction="column">
          <Grid item>
            <Typography>Maximum Volume</Typography>
            <Slider
              value={typeof _maxVolume === 'number' ? _maxVolume : 0}
              onChange={handleMaxVolumeChange}
              onChangeCommitted={updateMaxVolume}
              marks={marks}
              max={100}
              min={0}
              size="small"
              step={5}
              valueLabelDisplay="auto"
            />
          </Grid>

          <Grid item>
            <Typography>Volume Steps</Typography>
            <Slider
              defaultValue={volumeStep}
              marks
              max={15}
              min={1}
              size="small"
              step={1}
              valueLabelDisplay="auto"
            />
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};

export default SettingsVolume;
