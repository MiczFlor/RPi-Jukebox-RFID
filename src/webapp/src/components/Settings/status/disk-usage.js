import React, { useEffect, useState } from 'react';

import {
  ListItem,
  ListItemText,
  LinearProgress,
} from '@mui/material';

import request from '../../../utils/request';
import { Box } from '@mui/system';

const StatusDiskUsage = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [primaryText, setPrimaryText] = useState(undefined);
  const [diskUsage, setDiskUsage] = useState(0);

  const calcPercantage = ({ used, total }) => (
    parseInt((used/total * 100))
  );

  const calcMbToGb = (value) => (
    (value/1000).toFixed(1)
  );

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      const { result, error } = await request('getDiskUsage');

      if(result) {
        setDiskUsage(calcPercantage(result));

        const text = ` ${calcMbToGb(result?.used)} GB of ${calcMbToGb(result?.total)} GB used (${calcPercantage(result)}%)`;
        setPrimaryText(text);
      }
      if(error) {
        setPrimaryText('⚠️ Disk usage could not be loaded.')
        console.error(error);
      };
      setIsLoading(false);
    }

    fetchData();
  }, []);

  return (
    <ListItem
      disableGutters
      sx={{ display: 'flex', flexDirection: 'column', }}
    >
      <Box sx={{ width: '100%' }}>
        <LinearProgress variant="determinate" value={diskUsage} />
      </Box>
      <ListItemText
        sx={{ width: '100%' }}
        primary={isLoading ? 'Loading ...' : primaryText}
        secondary="Disk usage"
      />
    </ListItem>
  );
};

export default StatusDiskUsage;
