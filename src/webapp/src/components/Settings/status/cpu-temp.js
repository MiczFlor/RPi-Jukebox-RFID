import React, { useContext } from 'react';

import {
  ListItem,
  ListItemText,
} from '@mui/material';

import PubSubContext from '../../../context/pubsub/context';

const StatusCpuTemp = () => {
  const { state: {
    'host.timer.cputemp': hostTimerCputemp,
    'host.temperature.cpu': hostTemperatureCpu
  } } = useContext(PubSubContext);

  let primaryText = 'Unavailable';

  if (typeof hostTimerCputemp === 'object' && hostTimerCputemp !== null) {
    if (hostTimerCputemp?.enabled === true) {
      if (typeof hostTemperatureCpu === 'string' || hostTemperatureCpu instanceof String) {
        primaryText = `${hostTemperatureCpu}°C`;
      }
    }
    else {
      primaryText = 'Not enabled or not supported';
    }
  }

  return (
    <ListItem disableGutters>
      <ListItemText
        primary={primaryText}
        secondary="CPU Temperature"
      />
    </ListItem>
  );
};

export default StatusCpuTemp;
