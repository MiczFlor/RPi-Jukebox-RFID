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

import request from '../../utils/request';

const marks = [5, 25, 50, 75, 100].map(
  (value) => ({ value, label: `${value}%` })
);

const SettingsVolume = () => {
  // const [volumeStep] = useState(5);
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
      <CardHeader title="Volume" />
      <Divider />
      <CardContent>
        <Grid container direction="column">
          <Grid item>
            <Typography>Maximum Volume</Typography>
            <Slider
              value={typeof maxVolume === 'number' ? maxVolume : 0}
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
{/* TODO: Currently not implemented on the backend side!
          <Grid item>
            <Typography>Volume Steps</Typography>
            <Slider
              defaultValue={volumeStep}
              disabled={true}
              marks
              max={15}
              min={1}
              size="small"
              step={1}
              valueLabelDisplay="auto"
            />
          </Grid> */}
        </Grid>
      </CardContent>
    </Card>
  );
};

export default SettingsVolume;
