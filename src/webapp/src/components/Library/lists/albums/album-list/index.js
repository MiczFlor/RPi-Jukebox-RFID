import React from 'react';

import {
  List,
  Typography,
} from '@mui/material';

import AlbumListItem from './album-list-item';

const AlbumList = ({ albums, searchQuery }) => {
  if (albums?.length) {
    return (
      <List sx={{ width: '100%', bgcolor: 'background.paper' }}>
        {albums.map(AlbumListItem)}
      </List>
    );
  }

  if (searchQuery) return <Typography>☝️ No music found!</Typography>
  return <Typography>Your library is empty! 🙈</Typography>
}

export default React.memo(AlbumList);
