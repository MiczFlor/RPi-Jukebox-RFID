import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import {
  IconButton,
  ListItem,
  ListItemText,
} from '@mui/material';
import VolumeUpIcon from '@mui/icons-material/VolumeUp';

import request from '../../../utils/request';

const StatusIpAddress = () => {
  const { t } = useTranslation();

  const [isLoading, setIsLoading] = useState(true);
  const [primaryText, setPrimaryText] = useState(undefined);

  const sayIpAddress = () => request('say_my_ip');

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      const { result, error } = await request('getIpAddress');

      if(result) setPrimaryText(result);
      if(error) {
        setPrimaryText(`⚠️ ${t('settings.status.ip-address.loading-error')}`)
        console.error(error);
      };
      setIsLoading(false);
    }

    fetchData();
  }, [t]);

  return (
    <ListItem
      disableGutters
      secondaryAction={
        <IconButton
          aria-label={t('settings.status.ip-address.button-title')}
          edge="end"
          onClick={sayIpAddress}
        >
          <VolumeUpIcon />
        </IconButton>
      }
    >
      <ListItemText
        primary={isLoading ? `${t('general.loading')} ...` : primaryText}
        secondary={t('settings.status.ip-address.label')}
      />
    </ListItem>
  );
};

export default StatusIpAddress;
