import React from 'react';
import { useTranslation } from 'react-i18next';

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
  const { t } = useTranslation();

  return (
    <Card>
      <CardHeader
        title={t('settings.secondswipe.title')}
        subheader={t('settings.feature-not-enabled')}
      />
      <Divider />
      <CardContent>
        <Grid container direction="column">
          <Grid item>
            <RadioGroup aria-label="gender" name="gender1">
              <FormControlLabel
                value="restart"
                control={<Radio />}
                label={t('settings.secondswipe.restart')}
                disabled={true}
              />
              <FormControlLabel
                value="pause"
                control={<Radio />}
                label={t('settings.secondswipe.toggle')}
                disabled={true}
              />
              <FormControlLabel
                value="skipnext"
                control={<Radio />}
                label={t('settings.secondswipe.skip')}
                disabled={true}
              />
              <FormControlLabel
                value="noaudioplay"
                control={<Radio />}
                label={t('settings.secondswipe.ignore')}
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
