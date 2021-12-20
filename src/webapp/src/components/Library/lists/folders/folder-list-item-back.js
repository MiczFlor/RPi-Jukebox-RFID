import React from 'react';

import {
  ListItem,
  ListItemButton,
  ListItemText,
} from '@mui/material';

import ArrowBackIcon from '@mui/icons-material/ArrowBack';

import FolderLink from './folder-link';

const FolderListItemBack = ({ dir }) => {
  return (
    <ListItem disablePadding>
      <ListItemButton
        component={FolderLink}
        data={{ dir }}
        aria-label="back"
      >
        <ArrowBackIcon />
        <ListItemText primary={'..'} />
      </ListItemButton>
    </ListItem>
  );
}

export default FolderListItemBack;
