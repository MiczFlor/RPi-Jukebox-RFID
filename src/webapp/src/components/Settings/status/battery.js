import React, { useContext, useEffect, useState } from 'react';

import {
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
} from '@mui/material';

import BatteryIcon from '../helpers/battery-icon';
import PubSubContext from '../../../context/pubsub/context';
import { pluginIsLoaded } from '../../../utils/utils';

const StatusBattery = () => {
  const { state: {
    'core.plugins.loaded': plugins,
    'batt_status': { soc, charging } = {}
  } } = useContext(PubSubContext);

  const [batteryPluginAvaialble, setBatteryPluginAvailability] = useState(false);

  useEffect(() => {
    if (pluginIsLoaded(plugins, 'battmon')) {
      setBatteryPluginAvailability(true);
    }
  }, [plugins]);

  return (
    batteryPluginAvaialble &&
      <ListItem disableGutters>
        <ListItemAvatar>
          <Avatar>
            <BatteryIcon soc={soc} charging={charging} />
          </Avatar>
        </ListItemAvatar>
        <ListItemText
          primary={soc ? `${soc}%` : 'Loading ...'}
          secondary={soc ? `Battery is ${!charging ? 'not ' : ''}charging` : 'Battery'}
        />
      </ListItem>
  );
};

export default StatusBattery;
