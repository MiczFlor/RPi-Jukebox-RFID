import React from 'react';
import { useTranslation } from 'react-i18next';

import { useTheme } from '@mui/material/styles';

import {
  Card,
  CardContent,
  CardHeader,
  Divider,
  Grid,
} from '@mui/material';
import Timer from './timer';

const SettingsTimers = () => {
  const { t } = useTranslation();
  const theme = useTheme();
  const spacer = { marginBottom: theme.spacing(2) }

  return (
    <Card>
      <CardHeader
        title={t('settings.timers.title')}
      />
      <Divider />
      <CardContent>
        <Grid
          container
          direction="column"
          sx={{ '& > .MuiGrid-root:not(:last-child)': spacer }}
        >
          <Timer type={'shutdown'} />
          <Timer type={'stop-player'} />
          <Timer type={'fade-volume'} />
          {/* <Timer type={'idle-shutdown'} /> */}
        </Grid>
      </CardContent>
    </Card>
  );
};

export default SettingsTimers;
