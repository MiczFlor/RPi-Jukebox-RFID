import React, {
  useCallback,
  useEffect,
  useState,
} from "react";
import { useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

import {
  Alert,
  Box,
  CircularProgress,
  Typography,
} from "@mui/material";

import { listLibraryEntries } from '../../../../utils/library-api';
import CreateFolderDialog from './create-folder-dialog';
import DeleteEntriesDialog from './delete-entries-dialog';
import FolderList from "./folder-list";
import LibraryActions from './library-actions';
import UploadDialog from './upload-dialog';

import { ROOT_DIR } from '../../../../config';

const Folders = ({
  musicFilter,
  isSelecting,
  registerMusicToCard,
}) => {
  const { t } = useTranslation();
  const { dir = ROOT_DIR } = useParams();
  const [folders, setFolders] = useState([]);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [reloadNumber, setReloadNumber] = useState(0);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [deleteEntries, setDeleteEntries] = useState([]);
  const [operationWarning, setOperationWarning] = useState('');
  const [isManagementSelecting, setIsManagementSelecting] = useState(false);
  const [selectedPaths, setSelectedPaths] = useState(new Set());
  const [uploadFiles, setUploadFiles] = useState([]);
  const [isDragging, setIsDragging] = useState(false);
  const currentFolder = decodeURIComponent(dir);

  const search = ({ name }) => {
    if (musicFilter === '') return true;

    const lowerCaseMusicFilter = musicFilter.toLowerCase();

    return name.toLowerCase().includes(lowerCaseMusicFilter);
  };

  useEffect(() => {
    let isCurrent = true;
    const fetchFolderList = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const entries = await listLibraryEntries(currentFolder);
        if (isCurrent) setFolders(entries);
      }
      catch (requestError) {
        if (isCurrent) setError(requestError);
      }
      finally {
        if (isCurrent) setIsLoading(false);
      }
    }

    fetchFolderList();
    return () => {
      isCurrent = false;
    };
  }, [currentFolder, reloadNumber]);

  useEffect(() => {
    setIsManagementSelecting(false);
    setSelectedPaths(new Set());
  }, [currentFolder]);

  const reloadFolder = useCallback(() => {
    setReloadNumber((value) => value + 1);
  }, []);

  const handleFiles = (files) => {
    if (files.length) setUploadFiles(files);
  };

  const toggleSelected = ({ relpath }) => {
    setSelectedPaths((paths) => {
      const nextPaths = new Set(paths);
      if (nextPaths.has(relpath)) {
        nextPaths.delete(relpath);
      }
      else {
        nextPaths.add(relpath);
      }
      return nextPaths;
    });
  };

  const cancelSelection = () => {
    setIsManagementSelecting(false);
    setSelectedPaths(new Set());
  };

  const deleteSelected = () => {
    setDeleteEntries(folders.filter(({ relpath }) => selectedPaths.has(relpath)));
  };

  const deletionCompleted = (warning = '') => {
    setDeleteEntries([]);
    setOperationWarning(warning);
    cancelSelection();
    reloadFolder();
  };

  const folderCreated = () => {
    setCreateDialogOpen(false);
    reloadFolder();
  };

  const handleDrop = (event) => {
    event.preventDefault();
    setIsDragging(false);
    handleFiles(Array.from(event.dataTransfer.files || []));
  };

  const filteredFolders = folders.filter(search);

  return (
    <Box
      onDragEnter={(event) => {
        if (isSelecting) return;
        event.preventDefault();
        setIsDragging(true);
      }}
      onDragLeave={(event) => {
        if (event.currentTarget === event.target) setIsDragging(false);
      }}
      onDragOver={(event) => {
        if (!isSelecting) event.preventDefault();
      }}
      onDrop={(event) => {
        if (!isSelecting) handleDrop(event);
      }}
      sx={{
        minWidth: 0,
        outline: isDragging ? '2px dashed' : '2px solid transparent',
        outlineColor: isDragging ? 'primary.main' : 'transparent',
        outlineOffset: 4,
        width: '100%',
      }}
    >
      {!isSelecting &&
        <LibraryActions
          isSelecting={isManagementSelecting}
          onCancelSelection={cancelSelection}
          onCreateFolder={() => setCreateDialogOpen(true)}
          onDeleteSelected={deleteSelected}
          onFilesSelected={handleFiles}
          onStartSelection={() => setIsManagementSelecting(true)}
          selectedCount={selectedPaths.size}
        />
      }
      {isDragging &&
        <Alert severity="info" sx={{ marginBottom: 1 }}>
          {t('library.folders.manager.drop-files')}
        </Alert>
      }
      {operationWarning &&
        <Alert
          onClose={() => setOperationWarning('')}
          severity="warning"
          sx={{ marginBottom: 1 }}
        >
          {operationWarning}
        </Alert>
      }
      {isLoading && <CircularProgress />}
      {!isLoading && error &&
        <Typography>{t('library.loading-error')}</Typography>
      }
      {!isLoading && !error && musicFilter && !filteredFolders.length &&
        <Typography>{t('library.folders.no-music')}</Typography>
      }
      {!isLoading && !error && (!musicFilter || filteredFolders.length > 0) &&
        <FolderList
          dir={dir}
          folders={filteredFolders}
          isManagementSelecting={isManagementSelecting}
          isSelecting={isSelecting}
          onDelete={(entry) => setDeleteEntries([entry])}
          onToggleSelected={toggleSelected}
          registerMusicToCard={registerMusicToCard}
          selectedPaths={selectedPaths}
          showManagementActions={!isSelecting}
        />
      }
      <CreateFolderDialog
        folder={currentFolder}
        onClose={() => setCreateDialogOpen(false)}
        onCreated={folderCreated}
        open={createDialogOpen}
      />
      <DeleteEntriesDialog
        entries={deleteEntries}
        onClose={() => setDeleteEntries([])}
        onDeleted={deletionCompleted}
        open={deleteEntries.length > 0}
      />
      <UploadDialog
        files={uploadFiles}
        folder={currentFolder}
        onClose={() => setUploadFiles([])}
        onLibraryChanged={reloadFolder}
        open={uploadFiles.length > 0}
      />
    </Box>
  );
};

export default Folders;
