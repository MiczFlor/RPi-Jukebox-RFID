import React from 'react';

import {
  Grid,
  FormControl,
  FormControlLabel,
  Radio,
  RadioGroup,
  Typography,
} from '@mui/material';

import {
  getActionAndCommand,
  getArgsValues,
} from '../../../utils';


const SayMyIpOptions = ({
  actionData,
  handleActionDataChange,
}) => {
  const { action, command } = getActionAndCommand(actionData);
  const [option] = getArgsValues(actionData);

  const onChange = (event, option) => {
    handleActionDataChange(action, command, { option })
  };

  return (
    <Grid container alignItems="center" sx={{ marginTop: '20px' }}>
      <Grid item xs={12}>
        <Typography>Do you want to hear the full IP address or just the last quadrant?</Typography>
        <FormControl component="fieldset">
          <RadioGroup
            aria-label="gender"
            name="controlled-radio-buttons-group"
            value={option || 'full'}
            onChange={onChange}
          >
            <FormControlLabel value="full" control={<Radio />} label="Full (e.g. 192.168.1.53)" />
            <FormControlLabel value="short" control={<Radio />} label="Short (e.g. 53)" />
          </RadioGroup>
        </FormControl>
      </Grid>
    </Grid>
  );
};

export default SayMyIpOptions;
