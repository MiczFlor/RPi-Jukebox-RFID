import React, { useEffect, useState } from 'react';

import {
  CircularProgress,
  Grid,
  TextField,
  Typography,
} from '@mui/material';


import LibraryList from './library-list';

import { fetchDirectoryTreeOfAudiofolder } from '../../utils/requests';

const Library = () => {
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
          : <LibraryList folders={folders.filter(directoryNameBySearchQuery)} />
        }
        {error &&
          <Typography>An error occurred while loading the library.</Typography>
        }
      </Grid>
    </div>
  );
};

export default Library;
