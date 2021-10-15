import React, { useContext } from 'react';
import { Link } from 'react-router-dom';

import {
  Avatar,
  Divider,
  List,
  ListItem,
  ListItemAvatar,
  ListItemButton,
  ListItemText,
  Typography,
} from '@mui/material';

import noCover from '../../assets/noCover.jpg';
import PlayerContext from '../../context/player/context';

const LibraryItem = ({ directory, play }) => {
  const tree = directory.split('/');
  const folder = tree.pop();
  const parentPath = tree.join('/');

  return (
    <>
      <ListItem disablePadding>
        <ListItemButton onClick={e => play(directory)}>
          <ListItemAvatar>
            <Avatar variant="rounded" alt="Cover" src={noCover} />
          </ListItemAvatar>
          <ListItemText
            primary={folder}
            secondary={parentPath}
          />
        </ListItemButton>
      </ListItem>
      <Divider component="li" />
    </>
  );
}

const LibraryList = ({ folders }) => {
  const { play } = useContext(PlayerContext);

  return folders?.length
    ? <List sx={{ width: '100%', bgcolor: 'background.paper' }}>
        {folders
          .map(({ directory }) =>
            <LibraryItem
              directory={directory}
              key={directory}
              play={play}
            />
          )
        }
      </List>
    : <Typography>Your library is empty!</Typography>
}

export default React.memo(LibraryList);
