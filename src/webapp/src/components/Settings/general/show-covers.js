import React, { useContext } from 'react';
import { useTranslation } from 'react-i18next';

import {
  Box,
  Grid,
  Switch,
  Typography,
} from '@mui/material';

import AppSettingsContext from '../../../context/appsettings/context';
import request from '../../../utils/request';

const ShowCovers = () => {
  const { t } = useTranslation();

  const {
    settings,
    setSettings,
  } = useContext(AppSettingsContext);

  const {
    show_covers,
  } = settings;

  const updateShowCoversSetting = async (show_covers) => {
    await request('setAppSettings', { settings: { show_covers }});
  }

  const handleSwitch = (event) => {
    setSettings({ show_covers: event.target.checked});
    updateShowCoversSetting(event.target.checked);
  }

  return (
    <Grid container direction="column" justifyContent="center">
      <Grid container direction="row" justifyContent="space-between" alignItems="center">
        <Typography>
          {t(`settings.general.show_covers.title`)}
        </Typography>
        <Box sx={{
          display: 'flex',
          alignItems: 'center',
          marginLeft: '0',
        }}>
          <Switch
            checked={show_covers}
            onChange={handleSwitch}
          />
        </Box>
      </Grid>
    </Grid>
  );
};

export default ShowCovers;
