import { List } from '@mui/material';

import AlbumListItem from '../../../../Library/lists/albums/album-list/album-list-item'
import NoMusicSelected from './no-music-selected';

const SelectedAlbum = ({ values: [albumartist, album, content_uri, provider] }) => {
  if (albumartist && album) {
    return (
      <List sx={{ width: '100%' }}>
        <AlbumListItem
          albumartist={albumartist}
          album={album}
          content_uri={content_uri}
          isButton={false}
          provider={provider}
        />
      </List>
    );
  }

  return <NoMusicSelected />
};

export default SelectedAlbum;
