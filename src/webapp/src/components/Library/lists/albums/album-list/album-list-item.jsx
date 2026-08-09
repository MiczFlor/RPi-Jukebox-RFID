import { forwardRef, useContext, useEffect, useState } from 'react';
import {
  Link,
  useLocation,
} from 'react-router-dom';
import { useTranslation } from 'react-i18next';

import {
  Avatar,
  Checkbox,
  ListItem,
  ListItemAvatar,
  ListItemButton,
  ListItemIcon,
  ListItemText,
} from '@mui/material';

import noCover from '../../../../../assets/noCover.jpg';

import AppSettingsContext from '../../../../../context/appsettings/context';
import request from '../../../../../utils/request';

const AlbumListItem = ({
  albumartist,
  album,
  content_type,
  content_uri,
  cover_url,
  isButton = true,
  isManagementSelecting = false,
  isSelected = false,
  onToggleSelected,
  provider = 'mpd',
  view = 'albums',
}) => {
  const { t } = useTranslation();
  const { search: urlSearch } = useLocation();
  const [coverImage, setCoverImage] = useState(cover_url || noCover);

  const {
    settings,
  } = useContext(AppSettingsContext);

  const {
    show_covers,
  } = settings;

  useEffect(() => {
    const getCoverArt = async () => {
      const { result } = await request('getAlbumCoverArt', {
        albumartist,
        album,
        content_uri,
        provider,
      });
      if (result) {
        if(result !== 'CACHE_PENDING') {
          setCoverImage(result.startsWith('http') ? result : `/cover-cache/${result}`);
        }
      };
    }

    setCoverImage(cover_url || noCover);
    if (cover_url) {
      setCoverImage(cover_url);
    }
    else if (albumartist && album && show_covers) {
      getCoverArt();
    }
  }, [albumartist, album, content_uri, cover_url, provider, show_covers]);

  const AlbumLink = forwardRef((props, ref) => {
    const artist = encodeURIComponent(albumartist || t('library.albums.unknown-artist'));
    const encodedAlbum = encodeURIComponent(album || t('library.albums.unknown-album'));

    const searchParams = new URLSearchParams(urlSearch);
    if (content_uri) searchParams.set('content_uri', content_uri);
    else searchParams.delete('content_uri');
    const search = searchParams.toString();
    const location = [
      `/library/${provider}/${view}/${artist}/${encodedAlbum}`,
      search ? `?${search}` : '',
    ].join('');

    return <Link ref={ref} to={location} {...props} />
  });
  AlbumLink.displayName = 'AlbumLink';

  const content = (
    <>
      {show_covers &&
        <ListItemAvatar>
          <Avatar variant="rounded" alt="Cover" src={coverImage} />
        </ListItemAvatar>
      }
      <ListItemText
        primary={album || t('library.albums.unknown-album')}
        secondary={[
          albumartist,
          provider === 'spotify'
            ? t(`library.albums.spotify-${content_type || 'album'}`)
            : null,
        ].filter(Boolean).join(' · ') || null}
      />
    </>
  );

  return (
    <ListItem
      disablePadding={isButton || isManagementSelecting}
      key={content_uri || album}
    >
      {isManagementSelecting
        ? (
          <ListItemButton
            onClick={() => onToggleSelected({
              album,
              albumartist,
              content_type,
              content_uri,
              cover_url,
              provider,
            })}
            selected={isSelected}
            sx={{ minHeight: 56 }}
          >
            <ListItemIcon sx={{ minWidth: 44 }}>
              <Checkbox
                checked={isSelected}
                edge="start"
                slotProps={{
                  input: {
                    'aria-label': t('library.spotify.manager.select-item', {
                      name: album,
                    }),
                  },
                }}
                tabIndex={-1}
              />
            </ListItemIcon>
            {content}
          </ListItemButton>
        )
        : isButton
        ? (
          <ListItemButton component={AlbumLink} nativeButton={false}>
            {content}
          </ListItemButton>
        )
        : content
      }
    </ListItem>
  );
}

export default AlbumListItem;
