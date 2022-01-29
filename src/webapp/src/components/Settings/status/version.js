import React, { useContext } from 'react';
import { useTranslation } from 'react-i18next';

import {
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
} from '@mui/material';

import FavoriteIcon from '@mui/icons-material/Favorite';

import PubSubContext from '../../../context/pubsub/context';

const StatusVersion = () => {
  const { t } = useTranslation();

  const { state: { 'core.version': coreVersion } } = useContext(PubSubContext);

  return (
    <ListItem disableGutters>
      <ListItemAvatar>
        <Avatar>
          <FavoriteIcon />
        </Avatar>
      </ListItemAvatar>
      <ListItemText
        primary={coreVersion ? `${coreVersion}` : `${t('general.loading')} ...`}
        secondary={t('settings.status.version.label')}
      />
    </ListItem>
  );
};

export default StatusVersion;
