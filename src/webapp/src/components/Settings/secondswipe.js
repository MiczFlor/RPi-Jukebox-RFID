import React from 'react';

import {
  Card,
  CardContent,
  CardHeader,
  Divider,
  FormControlLabel,
  Grid,
  Radio,
  RadioGroup,
} from '@mui/material';

const SettingsSecondSwipe = () => {
  return (
    <Card>
      <CardHeader title="Second Swipe" />
      <Divider />
      <CardContent>
        <Grid container direction="column">
          <Grid item>
            <RadioGroup aria-label="gender" name="gender1">
              <FormControlLabel value="restart" control={<Radio />} label="Re-start playlist" />
              <FormControlLabel value="pause" control={<Radio />} label="Toggle pause / play" />
              <FormControlLabel value="skipnext" control={<Radio />} label="Skip to next track" />
              <FormControlLabel value="noaudioplay" control={<Radio />} label="Ignore audio playout triggers, only system commands" />
            </RadioGroup>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};

export default SettingsSecondSwipe;
