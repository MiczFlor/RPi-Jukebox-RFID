import React from 'react';
import { useTranslation } from 'react-i18next';

import {
  Card,
  CardContent,
  CardHeader,
  Divider,
  Grid,
  List,
} from '@mui/material';
import Timer from './timer';

const SettingsTimers = () => {
  const { t } = useTranslation();

  return (
    <Card>
      <CardHeader
        title={t('settings.timers.title')}
      />
      <Divider />
      <CardContent>
        <Grid item xs={12}>
          <List>
            <Timer type={'fade-volume'} />
            <Timer type={'shutdown'} />
            <Timer type={'stop-player'} />
            <Timer type={'idle-shutdown'} />
          </List>
        </Grid>
      </CardContent>
    </Card>
  );
};

export default SettingsTimers;
