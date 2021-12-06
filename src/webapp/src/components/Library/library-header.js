import React, { useState } from "react";
import {
  useNavigate,
  useParams,
} from 'react-router-dom';
import {
  Grid,
  IconButton,
  Stack,
  Switch,
  TextField,
  Typography,
} from "@mui/material";

import SearchIcon from '@mui/icons-material/Search';

const LibraryHeader = ({ handleSearch, searchQuery }) => {
  const navigate = useNavigate();
  const { '*': view } = useParams();
  const [showSearchInput, setShowSearchInput] = useState(false);

  const getCurrentView = () => (
    view.startsWith('folders') ? 'folders' : 'albums'
  );

  const toggleView = () => {
    const path = view.startsWith('folders') ? 'albums' : 'folders';
    localStorage.setItem('libraryLastListView', path);
    navigate(path);
  };

  return (
    <Grid container sx={{ marginBottom: '8px' }}>
      <Grid item
        xs={12}
        sx={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between', width: '100%' }}
      >
        <IconButton
          aria-label="Toggle Search Input"
          onClick={() => setShowSearchInput(!showSearchInput)}
          color={showSearchInput ? 'primary' : undefined}
        >
          <SearchIcon />
        </IconButton>
        {showSearchInput &&
          <TextField
            id="library-search"
            label="Search"
            onChange={handleSearch}
            value={searchQuery}
            variant="outlined"
            size="small"
            autoFocus
            focused
            sx={{
              width: '100%',
            }}
          />
        }
        {!showSearchInput &&
          <Stack
            alignItems="center"
            direction="row"
            sx={{ marginRight: '5px' }}
          >
            <Typography
              color={getCurrentView() === 'albums' && 'primary'}
              sx={{ transition: 'color .25s' }}
            >
              Albums
            </Typography>
            <Switch
              checked={getCurrentView() === 'folders' ? true : false}
              onChange={toggleView}
              inputProps={{ 'aria-label': 'Toggle Album/Folder view' }}
              color="default"
            />
            <Typography
              color={getCurrentView() === 'folders' && 'primary'}
              sx={{ transition: 'color .25s' }}
            >
              Folders
            </Typography>
          </Stack>
        }
      </Grid>
    </Grid>
  );
}

export default LibraryHeader;
