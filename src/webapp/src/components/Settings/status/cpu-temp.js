import React, { useContext } from 'react';

import {
  ListItem,
  ListItemText,
} from '@mui/material';

import PubSubContext from '../../../context/pubsub/context';

const StatusCpuTemp = () => {
  const { state: { 'host.timer.cputemp': cpuTemp } } = useContext(PubSubContext);

  let temperature = 'Not available';

  // Backend sends object when CPU Temp is disabled in jukebox.yaml
  // or not supported in backend (e.g. when using Docker)
  if (typeof cpuTemp === 'object' && cpuTemp !== null) {
    if (cpuTemp?.enabled === false) {
      temperature = 'Functionality not enabled or not supported'
    }
  }

  // Backend sense string when temperature is available
  if (typeof cpuTemp === 'string' || cpuTemp instanceof String) {
    temperature = `${cpuTemp}°C`;
  }

  return (
    <ListItem disableGutters>
      <ListItemText
        primary={temperature}
        secondary="CPU Temperature"
      />
    </ListItem>
  );
};

export default StatusCpuTemp;
