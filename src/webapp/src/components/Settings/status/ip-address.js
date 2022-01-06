import React, { useEffect, useState } from 'react';

import {
  ListItem,
  ListItemText,
} from '@mui/material';

import request from '../../../utils/request';

const StatusIpAddress = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [primaryText, setPrimaryText] = useState(undefined);

  useEffect(() => {
    const fetchIpAddress = async () => {
      setIsLoading(true);
      const { result, error } = await request('getIpAddress');

      if(result) setPrimaryText(result);
      if(error) {
        setPrimaryText('⚠️ IP address could not be loaded.')
        console.error(error);
      };
      setIsLoading(false);
    }

    fetchIpAddress();
  }, []);

  return (
    <ListItem disableGutters>
      <ListItemText
        primary={isLoading ? 'Loading ...' : primaryText}
        secondary="IP address"
      />
    </ListItem>
  );
};

export default StatusIpAddress;
