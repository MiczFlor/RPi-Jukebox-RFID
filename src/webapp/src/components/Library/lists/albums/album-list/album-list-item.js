import React, { forwardRef } from 'react';
import { Link } from 'react-router-dom';

import {
  Avatar,
  ListItem,
  ListItemAvatar,
  ListItemButton,
  ListItemText,
} from '@mui/material';

import noCover from '../../../../../assets/noCover.jpg';
import { LABELS } from '../../../../../config';

const AlbumListItem = ({ albumartist, album }) => {
  const AlbumLink = forwardRef((props, ref) => {
    const { data } = props;

    const artist = encodeURIComponent(data?.albumartist || LABELS.UNKNOW_ARTIST);
    const album = encodeURIComponent(data?.album || LABELS.UNKNOW_ALBUM);

    // TODO: Introduce fallback incase artist or album are undefined
    const location = {
      pathname: `/library/albums/${artist}/${album}`,
    };

    return <Link ref={ref} to={location} {...props} />
  });

  return (
    <ListItem
      button
      component={AlbumLink}
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
