import { useEffect, useState } from "react";
import {
  useLocation,
  useNavigate,
} from 'react-router-dom';
import { useTranslation } from 'react-i18next';

import {
  Alert,
  Box,
  CircularProgress,
  Typography,
} from "@mui/material";

import request from '../../../../utils/request';
import {
  addSpotifyLibraryItem,
  getSpotifyLibrary,
  removeSpotifyLibraryItems,
} from '../../../../utils/spotify-api';
import { flatByAlbum } from '../../../../utils/utils';

import AlbumList from "./album-list";
import AddSpotifyItemDialog from '../spotify/add-item-dialog';
import DeleteSpotifyItemsDialog from '../spotify/delete-items-dialog';
import SpotifyLibraryActions from '../spotify/library-actions';

const SPOTIFY_VIEWS = {
  album: 'albums',
  playlist: 'playlists',
  track: 'tracks',
};

const Albums = ({
  contentTypes,
  isSelecting = false,
  musicFilter,
  provider,
  view,
}) => {
  const { t } = useTranslation();
  const { search: urlSearch } = useLocation();
  const navigate = useNavigate();

  const [albums, setAlbums] = useState([]);
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [catalogError, setCatalogError] = useState(null);
  const [deleteItems, setDeleteItems] = useState([]);
  const [isManagementSelecting, setIsManagementSelecting] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [library, setLibrary] = useState(null);
  const [libraryError, setLibraryError] = useState(null);
  const [reloadNumber, setReloadNumber] = useState(0);
  const [selectedUris, setSelectedUris] = useState(new Set());

  const search = ({ albumartist, album }) => {
    if (musicFilter === '') return true;

    const lowerCaseMusicFilter = musicFilter.toLowerCase();

    return (albumartist || '').toLowerCase().includes(lowerCaseMusicFilter) ||
      (album || '').toLowerCase().includes(lowerCaseMusicFilter);
  };

  const contentTypesKey = contentTypes?.join(',') || '';

  useEffect(() => {
    let isCurrent = true;
    const fetchAlbumList = async () => {
      setIsLoading(true);
      setCatalogError(null);
      const { result, error } = await request('libraryItems', {
        provider,
        content_types: contentTypesKey ? contentTypesKey.split(',') : undefined,
      });
      if (!isCurrent) return;
      setIsLoading(false);

      if(result) setAlbums(result.reduce(flatByAlbum, []));
      if(error) setCatalogError(error);
    }

    fetchAlbumList();
    return () => {
      isCurrent = false;
    };
  }, [contentTypesKey, provider, reloadNumber]);

  useEffect(() => {
    let isCurrent = true;
    if (provider !== 'spotify') {
      setLibrary(null);
      return undefined;
    }
    const fetchLibrary = async () => {
      try {
        const nextLibrary = await getSpotifyLibrary();
        if (isCurrent) {
          setLibrary(nextLibrary);
          setLibraryError(null);
        }
      }
      catch (requestError) {
        if (isCurrent) setLibraryError(requestError);
      }
    };
    fetchLibrary();
    return () => {
      isCurrent = false;
    };
  }, [provider, reloadNumber]);

  useEffect(() => {
    setIsManagementSelecting(false);
    setSelectedUris(new Set());
  }, [contentTypesKey, provider]);

  const reload = () => setReloadNumber((value) => value + 1);

  const addItem = async (link) => {
    const { item } = await addSpotifyLibraryItem(link);
    setAddDialogOpen(false);
    const targetView = SPOTIFY_VIEWS[item.content_type] || 'albums';
    if (targetView === view) {
      reload();
    }
    else {
      navigate(`/library/${provider}/${targetView}${urlSearch}`);
    }
  };

  const cancelSelection = () => {
    setIsManagementSelecting(false);
    setSelectedUris(new Set());
  };

  const toggleSelected = (item) => {
    setSelectedUris((uris) => {
      const nextUris = new Set(uris);
      if (nextUris.has(item.content_uri)) {
        nextUris.delete(item.content_uri);
      }
      else {
        nextUris.add(item.content_uri);
      }
      return nextUris;
    });
  };

  const selectedItems = albums.filter(
    ({ content_uri: contentUri }) => selectedUris.has(contentUri),
  );

  const removeItems = async (items) => {
    await removeSpotifyLibraryItems(items.map(({ content_uri }) => content_uri));
    setDeleteItems([]);
    cancelSelection();
    reload();
  };

  const filteredAlbums = albums.filter(search);
  const showManagement = (
    provider === 'spotify' &&
    library?.mode === 'curated' &&
    !isSelecting
  );

  return (
    <Box sx={{ width: '100%' }}>
      {showManagement &&
        <SpotifyLibraryActions
          isSelecting={isManagementSelecting}
          onAdd={() => setAddDialogOpen(true)}
          onCancelSelection={cancelSelection}
          onDeleteSelected={() => setDeleteItems(selectedItems)}
          onStartSelection={() => setIsManagementSelecting(true)}
          selectedCount={selectedUris.size}
        />
      }
      {libraryError &&
        <Alert severity="error" sx={{ marginBottom: 1 }}>
          {libraryError.message}
        </Alert>
      }
      {isLoading
        ? <CircularProgress />
        : <AlbumList
            albums={filteredAlbums}
            isManagementSelecting={isManagementSelecting}
            musicFilter={musicFilter}
            onToggleSelected={toggleSelected}
            selectedUris={selectedUris}
            view={view}
      />}
      {catalogError &&
        <Typography>{t('library.loading-error')}</Typography>
      }
      <AddSpotifyItemDialog
        onAdd={addItem}
        onClose={() => setAddDialogOpen(false)}
        open={addDialogOpen}
      />
      <DeleteSpotifyItemsDialog
        items={deleteItems}
        onClose={() => setDeleteItems([])}
        onDelete={removeItems}
        open={deleteItems.length > 0}
      />
    </Box>
  );
};

export default Albums;
