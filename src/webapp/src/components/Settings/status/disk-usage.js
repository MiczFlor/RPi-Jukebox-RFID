import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import {
  ListItem,
  ListItemText,
  LinearProgress,
} from '@mui/material';

import request from '../../../utils/request';
import { Box } from '@mui/system';

const StatusDiskUsage = () => {
  const { t } = useTranslation();

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

        const text = t(
          'settings.status.disk-usage.result',
          {
            used: calcMbToGb(result?.used),
            total: calcMbToGb(result?.total),
            result: calcPercantage(result)
          }
        );
        setPrimaryText(text);
      }
      if(error) {
        setPrimaryText(`⚠️ ${t('settings.status.disk-usage.loading-error')}`)
        console.error(error);
      };
      setIsLoading(false);
    }

    fetchData();
  }, [t]);

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
        primary={isLoading ? `${t('general.loading')} ...` : primaryText}
        secondary={t('settings.status.disk-usage.label')}
      />
    </ListItem>
  );
};

export default StatusDiskUsage;
