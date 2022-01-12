import React from 'react';
import { useTranslation } from 'react-i18next';

import {
  Card,
  CardContent,
  CardHeader,
  Divider,
  Grid,
  InputLabel,
  NativeSelect,
} from '@mui/material';

const SettingsTimers = () => {
  const { t } = useTranslation();

  const TIMESLOTS = [0, 2, 5, 10, 15, 20, 30, 45, 60, 120, 180, 240];

  const options = TIMESLOTS.map(
    (value) => {
      if (value === 0) {
        return {
          value,
          label: t('settings.timers.option-label-off')
        };
      }

      return {
        value,
        label: t('settings.timers.option-label-timeslot', { value })
      };
    }
  );

  return (
    <Card>
      <CardHeader
        title={t('settings.timers.title')}
        subheader={t('settings.feature-not-enabled')}
      />
      <Divider />
      <CardContent>
        <Grid container direction="column">
          <Grid
            container
            direction="row"
            justifyContent="space-between"
            alignItems="center"
          >
            <Grid item>
              <InputLabel htmlFor="stopPlayoutTimer">
              {t('settings.timers.stop-playout-timer')}
              </InputLabel>
            </Grid>
            <Grid item>
              <NativeSelect
                disabled={true}
                id="stopPlayoutTimer"
                name="stopPlayoutTimer"
              >
                {options.map(({ value, label }) => (
                  <option key={value} value={value}>{label}</option>
                ))}
              </NativeSelect>
            </Grid>
          </Grid>

          <Grid
            container
            direction="row"
            justifyContent="space-between"
            alignItems="center"
          >
            <Grid item>
              <InputLabel htmlFor="shutdownTimer">
                {t('settings.timers.shutdown-timer')}
              </InputLabel>
            </Grid>
            <Grid item>
              <NativeSelect
                disabled={true}
                id="shutdownTimer"
                name="shutdownTimer"
              >
                {options.map(({ value, label }) => (
                  <option key={value} value={value}>{label}</option>
                ))}
              </NativeSelect>
            </Grid>
          </Grid>

          <Grid
            container
            direction="row"
            justifyContent="space-between"
            alignItems="center"
          >
            <Grid item>
              <InputLabel htmlFor="shutdownTimer">
                {t('settings.timers.idle-shutdown')}
              </InputLabel>
            </Grid>
            <Grid item>
              <NativeSelect
                disabled={true}
                id="shutdownTimer"
                name="shutdownTimer"
              >
                {options.map(({ value, label }) => (
                  <option key={value} value={value}>{label}</option>
                ))}
              </NativeSelect>
            </Grid>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};

export default SettingsTimers;
