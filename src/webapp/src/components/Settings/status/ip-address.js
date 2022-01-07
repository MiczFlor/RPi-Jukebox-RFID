import React, { useEffect, useState } from 'react';

import {
  IconButton,
  ListItem,
  ListItemText,
} from '@mui/material';
import VolumeUpIcon from '@mui/icons-material/VolumeUp';

import request from '../../../utils/request';

const StatusIpAddress = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [primaryText, setPrimaryText] = useState(undefined);

  const sayIpAddress = () => (
    request('say_my_ip_long')
  );

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      const { result, error } = await request('getIpAddress');

      if(result) setPrimaryText(result);
      if(error) {
        setPrimaryText('⚠️ IP address could not be loaded.')
        console.error(error);
      };
      setIsLoading(false);
    }

    fetchData();
  }, []);

  return (
    <ListItem
      disableGutters
      secondaryAction={
        <IconButton
          aria-label="Say my IP address"
          edge="end"
          onClick={sayIpAddress}
        >
          <VolumeUpIcon />
        </IconButton>
      }
    >
      <ListItemText
        primary={isLoading ? 'Loading ...' : primaryText}
        secondary="IP address"
      />
    </ListItem>
  );
};

export default StatusIpAddress;
