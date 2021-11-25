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
      <CardHeader
        title="Second Swipe"
        subheader="🚧 This feature is not yet enabled."
      />
      <Divider />
      <CardContent>
        <Grid container direction="column">
          <Grid item>
            <RadioGroup aria-label="gender" name="gender1">
              <FormControlLabel
                value="restart"
                control={<Radio />}
                label="Re-start playlist"
                disabled={true}
              />
              <FormControlLabel
                value="pause"
                control={<Radio />}
                label="Toggle pause / play"
                disabled={true}
              />
              <FormControlLabel
                value="skipnext"
                control={<Radio />}
                label="Skip to next track"
                disabled={true}
              />
              <FormControlLabel
                value="noaudioplay"
                control={<Radio />}
                label="Ignore audio playout triggers, only system commands"
                disabled={true}
              />
            </RadioGroup>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};

export default SettingsSecondSwipe;
