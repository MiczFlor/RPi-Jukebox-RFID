import React, { useContext } from 'react';

import {
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
} from '@mui/material';

import FavoriteIcon from '@mui/icons-material/Favorite';

import PubSubContext from '../../../context/pubsub/context';

const StatusVersion = () => {
  const { state: { 'core.version': coreVersion } } = useContext(PubSubContext);

  return (
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
  );
};

export default StatusVersion;
