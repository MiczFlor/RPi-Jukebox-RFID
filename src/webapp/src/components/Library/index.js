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
  Typography,
} from '@mui/material';

import noCover from '../../assets/noCover.jpg';
import PlayerContext from '../../context/player/context';

import { fetchDirectoryTreeOfAudiofolder } from '../../utils/requests';

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

  const [folders, setFolders] = useState([]);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
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
      setIsLoading(true);
      const { result, error } = await fetchDirectoryTreeOfAudiofolder();
      setIsLoading(false);

      if(result) setFolders(result.filter(entry => !!entry.directory));
      if(error) setError(error);
    }

    getFlattenListOfDirectories();
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
      <Grid
        container
        spacing={1}
        sx={{
          display: 'flex',
          justifyContent: 'center',
        }}
      >
        {isLoading
          ? <CircularProgress />
          : <List sx={{ width: '100%', bgcolor: 'background.paper' }}>
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
        {error &&
          <Typography>An error occurred while loading the library.</Typography>
        }
      </Grid>
    </div>
  );
};

export default Library;
