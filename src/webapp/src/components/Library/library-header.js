import React, { useState } from "react";
import {
  useLocation,
  useNavigate,
  useParams,
} from 'react-router-dom';
import { useTranslation } from 'react-i18next';

import {
  Grid,
  IconButton,
  Stack,
  Switch,
  TextField,
  Typography,
} from "@mui/material";

import SearchIcon from '@mui/icons-material/Search';

const LibraryHeader = ({ handleMusicFilter, musicFilter }) => {
  const { search: urlSearch } = useLocation();
  const navigate = useNavigate();
  const { '*': view } = useParams();
  const { t } = useTranslation();
  const [showSearchInput, setShowSearchInput] = useState(false);

  const getCurrentView = () => (
    view.startsWith('folders') ? 'folders' : 'albums'
  );

  const toggleView = () => {
    const path = view.startsWith('folders') ? 'albums' : 'folders';
    localStorage.setItem('libraryLastListView', path);
    navigate(`${path}${urlSearch}`);
  };

  const iconLabel = showSearchInput
    ? t('library.header.search-hide')
    : t('library.header.search-show');

  return (
    <Grid container sx={{ marginBottom: '8px' }}>
      <Grid item
        xs={12}
        sx={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between', width: '100%' }}
      >
        <IconButton
          aria-label={iconLabel}
          onClick={() => setShowSearchInput(!showSearchInput)}
          color={showSearchInput ? 'primary' : undefined}
          title={iconLabel}
        >
          <SearchIcon />
        </IconButton>
        {showSearchInput &&
          <TextField
            id="library-search"
            label={t('library.header.search-label')}
            onChange={handleMusicFilter}
            value={musicFilter}
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
              {t('library.header.albums')}
            </Typography>
            <Switch
              checked={getCurrentView() === 'folders' ? true : false}
              onChange={toggleView}
              inputProps={{ 'aria-label': t('library.header.toggle-label') }}
              color="default"
            />
            <Typography
              color={getCurrentView() === 'folders' && 'primary'}
              sx={{ transition: 'color .25s' }}
            >
              {t('library.header.folders')}
            </Typography>
          </Stack>
        }
      </Grid>
    </Grid>
  );
}

export default LibraryHeader;
