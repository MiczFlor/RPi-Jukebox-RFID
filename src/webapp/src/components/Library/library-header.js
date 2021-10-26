import React, { useState } from "react";

import {
  Grid,
  IconButton,
  Stack,
  Switch,
  TextField,
  Typography,
} from "@mui/material";

import SearchIcon from '@mui/icons-material/Search';

const LibraryHeader = ({ handleSearch, searchQuery, view, setView }) => {
  const [showSearchInput, setShowSearchInput] = useState(false);

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
              color={view === 'albums' && 'primary'}
              sx={{ transition: 'color .25s' }}
            >
              Albums
            </Typography>
            <Switch
              checked={view === 'folders' ? true : false}
              onChange={() => setView(view ==='folders' ? 'albums' : 'folders')}
              inputProps={{ 'aria-label': 'Toggle Album/Folder view' }}
              color="default"
            />
            <Typography
              color={view === 'folders' && 'primary'}
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
