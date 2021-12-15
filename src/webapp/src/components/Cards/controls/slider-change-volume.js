import React from 'react';

import {
  Grid,
  Slider,
  Stack,
  Typography,
} from '@mui/material';

import Remove from '@mui/icons-material/Remove';
import Add from '@mui/icons-material/Add';

const marks = [-10, -5, 0, 5, 10].map(
  (value) => ({ value, label: value })
);

const SliderChangeVolume = ({
  actionData,
  handleActionDataChange,
}) => {
  return (
    <Grid container alignItems="center">
      <Grid item xs={12}>
        <Typography>Volume Steps</Typography>
        <Stack spacing={2} direction="row" sx={{ mb: 1 }} alignItems="center">
          <Remove />
          <Slider
            aria-label="Volume steps"
            value={actionData.change_volume?.step || 0}
            marks={marks}
            step={1}
            min={-10}
            max={10}
            track={false}
            valueLabelDisplay="auto"
            onChange={(event, step) => handleActionDataChange('change_volume', { step })}
          />
          <Add />
        </Stack>
      </Grid>
    </Grid>
  );
};

export default SliderChangeVolume;
