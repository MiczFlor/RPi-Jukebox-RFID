import React, { useContext } from 'react';
import { useTranslation } from 'react-i18next';

import {
  ListItem,
  ListItemText,
} from '@mui/material';

import PubSubContext from '../../../context/pubsub/context';

const StatusCpuTemp = () => {
  const { t } = useTranslation();

  const { state: {
    'host.timer.cputemp': hostTimerCputemp,
    'host.temperature.cpu': hostTemperatureCpu
  } } = useContext(PubSubContext);

  let primaryText = t('settings.status.cpu-temp.unavailable');

  if (typeof hostTimerCputemp === 'object' && hostTimerCputemp !== null) {
    if (hostTimerCputemp?.enabled === true) {
      if (typeof hostTemperatureCpu === 'string' || hostTemperatureCpu instanceof String) {
        primaryText = `${hostTemperatureCpu}°C`;
      }
    }
    else {
      primaryText = t('settings.status.cpu-temp.not-enabled');
    }
  }

  return (
    <ListItem disableGutters>
      <ListItemText
        primary={primaryText}
        secondary={t('settings.status.cpu-temp.label')}
      />
    </ListItem>
  );
};

export default StatusCpuTemp;
