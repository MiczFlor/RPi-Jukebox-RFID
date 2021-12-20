import React from 'react';

import {
  List,
  Typography,
} from '@mui/material';

import AlbumListItem from './album-list-item';

const AlbumList = ({ albums, musicFilter }) => {
  if (albums?.length) {
    return (
      <List sx={{ width: '100%' }}>
        {albums.map(({ albumartist, album }, i) => (
          <AlbumListItem
            key={i}
            albumartist={albumartist}
            album={album}
          />
        ))}
      </List>
    );
  }

  if (musicFilter) return <Typography>☝️ No music found!</Typography>
  return <Typography>Your library is empty! 🙈</Typography>
}

export default React.memo(AlbumList);
