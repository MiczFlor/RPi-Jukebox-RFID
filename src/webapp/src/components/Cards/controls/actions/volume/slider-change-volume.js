import React from 'react';

import {
  Grid,
  Slider,
  Stack,
  Typography,
} from '@mui/material';

import Remove from '@mui/icons-material/Remove';
import Add from '@mui/icons-material/Add';

import {
  getActionAndCommand,
  getArgsValues,
} from '../../../utils';

const marks = [-10, -5, 0, 5, 10].map(
  (value) => ({ value, label: value })
);

const SliderChangeVolume = ({
  actionData,
  handleActionDataChange,
}) => {
  const { action, command } = getActionAndCommand(actionData);
  const [step] = getArgsValues(actionData);

  const onChange = (event, step) => {
    handleActionDataChange(action, command, { step })
  };

  return (
    <Grid container alignItems="center">
      <Grid item xs={12}>
        <Typography>Volume Steps</Typography>
        <Stack spacing={2} direction="row" sx={{ mb: 1 }} alignItems="center">
          <Remove />
          <Slider
            aria-label="Volume steps"
            value={step || 0}
            marks={marks}
            step={1}
            min={-10}
            max={10}
            track={false}
            valueLabelDisplay="auto"
            onChange={onChange}
          />
          <Add />
        </Stack>
      </Grid>
    </Grid>
  );
};

export default SliderChangeVolume;
