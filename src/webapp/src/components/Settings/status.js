import React, { useContext, useEffect, useState } from 'react';

import {
  Card,
  CardContent,
  CardHeader,
  Divider,
  Grid,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
} from '@mui/material';

import FavoriteIcon from '@mui/icons-material/Favorite';

import BatteryIcon from './helpers/battery-icon';
import PubSubContext from '../../context/pubsub/context';
import { pluginIsLoaded } from '../../utils/utils';

const SettingsStatus = () => {
  const { state: {
    'core.plugins.loaded': plugins,
    'core.version': coreVersion,
    'batt_status': { soc, charging } = {}
  } } = useContext(PubSubContext);

  const [batteryPluginAvaialble, setBatteryPluginAvailability] = useState(false);

  useEffect(() => {
    if (pluginIsLoaded(plugins, 'battmon')) {
      setBatteryPluginAvailability(true);
    }
  }, [plugins]);

  return (
    <Card>
      <CardHeader title="System Status" />
      <Divider />
      <CardContent>
        <Grid container>
          <Grid item xs={12}>
            <List>
              <ListItem disableGutters>
                <ListItemAvatar>
                  <Avatar>
                    <FavoriteIcon />
                  </Avatar>
                </ListItemAvatar>
                <ListItemText
                  primary={coreVersion ? `${coreVersion}` : 'Loading ...'}
                  secondary="Jukebox Core Version"
                />
              </ListItem>
              {batteryPluginAvaialble &&
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
              }
            </List>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};

export default SettingsStatus;
