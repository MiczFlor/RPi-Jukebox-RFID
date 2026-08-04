import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

import {
  Box,
  Button,
  CircularProgress,
  Stack,
  Typography,
} from '@mui/material';

import KeyboardArrowRightIcon from '@mui/icons-material/KeyboardArrowRight';

import request from '../../../utils/request';
import { flatByAlbum } from '../../../utils/utils';
import AlbumList from './albums/album-list';

const LibraryOverview = ({ musicFilter, sources }) => {
  const { t } = useTranslation();
  const [items, setItems] = useState([]);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchItems = async () => {
      setIsLoading(true);
      const { result, error: requestError } = await request('libraryItems');
      setIsLoading(false);
      if (result) setItems(result.reduce(flatByAlbum, []));
      if (requestError) setError(requestError);
    };
    fetchItems();
  }, []);

  const visibleItems = useMemo(() => {
    const query = musicFilter.toLowerCase();
    if (!query) return items;
    return items.filter(({ albumartist = '', album = '' }) => (
      albumartist.toLowerCase().includes(query) ||
      album.toLowerCase().includes(query)
    ));
  }, [items, musicFilter]);

  const groups = sources
    .flatMap((source) => source.views
      .filter((view) => (
        view.kind !== 'folders' && view.content_types?.length
      ))
      .map((view) => ({
        id: `${source.id}:${view.id}`,
        items: visibleItems.filter((item) => (
          item.provider === source.id &&
          view.content_types.includes(item.content_type || 'album')
        )),
        path: `/library/${source.id}/${view.id}`,
        provider: source.id,
        sourceLabel: t(`library.sources.${source.id}`, {
          defaultValue: source.label,
        }),
        view: view.id,
        viewLabel: t(`library.header.${view.id}`, {
          defaultValue: view.label,
        }),
      })))
    .filter(({ items: groupItems }) => groupItems.length);

  if (isLoading) return <CircularProgress />;
  if (error) return <Typography>{t('library.loading-error')}</Typography>;
  if (!groups.length) {
    return (
      <Typography>
        {musicFilter
          ? t('library.albums.no-music')
          : t('library.albums.empty-library')}
      </Typography>
    );
  }

  return (
    <Stack spacing={2} sx={{ width: '100%' }}>
      {groups.map((group) => (
        <Box component="section" key={group.id} sx={{ width: '100%' }}>
          <Stack
            direction="row"
            sx={{
              alignItems: 'center',
              justifyContent: 'space-between',
              paddingX: 1,
            }}
          >
            <Typography component="h2" variant="h6">
              {t('library.overview.group', {
                source: group.sourceLabel,
                view: group.viewLabel,
              })}
            </Typography>
            <Button
              component={Link}
              endIcon={<KeyboardArrowRightIcon />}
              size="small"
              to={group.path}
            >
              {t('library.overview.show-all')}
            </Button>
          </Stack>
          <AlbumList
            albums={group.items.slice(0, 5)}
            musicFilter={musicFilter}
            view={group.view}
          />
        </Box>
      ))}
    </Stack>
  );
};

export default LibraryOverview;
