import React, { useEffect, useState, useContext } from 'react';

import {
  Avatar,
  CircularProgress,
  Divider,
  Grid,
  List,
  ListItem,
  ListItemAvatar,
  ListItemButton,
  ListItemText,
  TextField,
} from '@mui/material';

import { socketRequest } from '../../sockets';
import noCover from '../../assets/noCover.jpg';
import PlayerContext from '../../context/player/context';

const DirectoryItem = ({ directory, play }) => {
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

const Library = () => {
  const { play } = useContext(PlayerContext);

  const [isLoading, setIsLoading] = useState(true);
  const [folders, setFolders] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = (event) => {
    setSearchQuery(event.target.value);
  };

  const directoryNameBySearchQuery = ({ directory }) => {
    if (searchQuery === '') return true;
    return directory.toLowerCase().includes(searchQuery.toLowerCase());
  };

  useEffect(() => {
    const getFlattenListOfDirectories = async () => {
      const list = await socketRequest('player', 'ctrl', 'list_all_dirs');

      setFolders(list.filter(entry => !!entry.directory));
    };

    getFlattenListOfDirectories();
    setIsLoading(false);
  }, []);

  return (
    <div id="library">
      <form noValidate autoComplete="off">
        <Grid container>
          <Grid item xs={12}>
            <TextField
              id="outlined-basic"
              label="Search"
              onChange={handleSearch}
              value={searchQuery}
              variant="outlined"
              sx={{
                width: '100%',
                marginBottom: '10px',
              }}
            />
          </Grid>
        </Grid>
      </form>
      {isLoading && <CircularProgress />}
      {!isLoading &&
        <List sx={{ width: '100%', bgcolor: 'background.paper' }}>
          {folders
            .filter(directoryNameBySearchQuery)
            .map(({ directory }) =>
              <DirectoryItem
                directory={directory}
                key={directory}
                play={play}
              />
            )
          }
        </List>
      }
    </div>
  );
};

export default Library;
