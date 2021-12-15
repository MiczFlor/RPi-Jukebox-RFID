import React, { forwardRef } from 'react';
import {
  Link,
  useLocation,
} from 'react-router-dom';

import {
  Avatar,
  ListItem,
  ListItemAvatar,
  ListItemButton,
  ListItemText,
} from '@mui/material';

import noCover from '../../../../../assets/noCover.jpg';
import { LABELS } from '../../../../../config';

const AlbumListItem = ({ albumartist, album, isButton = true }) => {
  const { search: urlSearch } = useLocation();

  const AlbumLink = forwardRef((props, ref) => {
    const { data } = props;

    const artist = encodeURIComponent(data?.albumartist || LABELS.UNKNOW_ARTIST);
    const album = encodeURIComponent(data?.album || LABELS.UNKNOW_ALBUM);

    // TODO: Introduce fallback incase artist or album are undefined
    const location = `${artist}/${album}${urlSearch}`;

    return <Link ref={ref} to={location} {...props} />
  });

  return (
    <ListItem
      button={isButton}
      component={isButton ? AlbumLink : null}
      data={{ albumartist, album }}
      disablePadding
      key={album}
    >
      <ListItemButton>
        <ListItemAvatar>
          <Avatar variant="rounded" alt="Cover" src={noCover} />
        </ListItemAvatar>
        <ListItemText
          primary={album || LABELS.UNKNOW_ALBUM}
          secondary={albumartist || null}
        />
      </ListItemButton>
    </ListItem>
  );
}

export default AlbumListItem;
