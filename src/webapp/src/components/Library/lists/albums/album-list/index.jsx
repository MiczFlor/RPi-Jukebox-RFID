import { memo } from 'react';
import { useTranslation } from 'react-i18next';

import {
  List,
  Typography,
} from '@mui/material';

import AlbumListItem from './album-list-item';

const AlbumList = ({
  albums,
  isManagementSelecting = false,
  musicFilter,
  onToggleSelected,
  selectedUris = new Set(),
  view,
}) => {
  const { t } = useTranslation();

  if (albums?.length) {
    return (
      <List sx={{ width: '100%' }}>
        {albums.map((entry, i) => (
          <AlbumListItem
            key={entry.content_uri || `${entry.provider}:${entry.albumartist}:${entry.album}:${i}`}
            isManagementSelecting={isManagementSelecting}
            isSelected={selectedUris.has(entry.content_uri)}
            onToggleSelected={onToggleSelected}
            view={view}
            {...entry}
          />
        ))}
      </List>
    );
  }

  if (musicFilter) return <Typography>{`☝️  ${t('library.albums.no-music')}`}</Typography>
  return <Typography>{`${t('library.albums.empty-library')} 🙈`}</Typography>
}

export default memo(AlbumList);
