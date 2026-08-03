import {
  useEffect,
  useMemo,
  useRef,
  useState,
} from 'react';
import { useTranslation } from 'react-i18next';

import {
  Alert,
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  Tooltip,
  Typography,
} from '@mui/material';

import CancelIcon from '@mui/icons-material/Cancel';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import ReplayIcon from '@mui/icons-material/Replay';

import {
  createLibraryFolder,
  refreshLibrary,
  translateLibraryError,
  uploadLibraryFile,
} from '../../../../utils/library-api';

const terminalStates = new Set(['cancelled', 'complete', 'failed']);

const joinLibraryPath = (folder, relativePath) => {
  if (!relativePath) return folder;
  if (folder === '.' || folder === './') return relativePath;
  return `${folder.replace(/\/+$/, '')}/${relativePath}`;
};

const parentAndName = (relativePath) => {
  const parts = relativePath.split('/');
  const name = parts.pop();
  return { name, parent: parts.join('/') };
};

const parentFolderPaths = (relativePath) => {
  const parts = relativePath.split('/');
  parts.pop();
  return parts.map((part, index) => parts.slice(0, index + 1).join('/'));
};

const UploadDialog = ({
  folder,
  onClose,
  onLibraryChanged,
  open,
  selection,
}) => {
  const { t } = useTranslation();
  const [queue, setQueue] = useState([]);
  const [currentId, setCurrentId] = useState(null);
  const [refreshError, setRefreshError] = useState('');
  const abortController = useRef(null);
  const batchNumber = useRef(0);
  const refreshedBatch = useRef(-1);

  useEffect(() => {
    if (!open) return;
    batchNumber.current += 1;
    refreshedBatch.current = -1;
    setRefreshError('');
    setCurrentId(null);
    setQueue([
      ...selection.folders.map((relativePath) => ({
        entryType: 'folder',
        error: '',
        id: `folder-${relativePath}`,
        progress: 0,
        relativePath,
        status: 'queued',
      })),
      ...selection.files.map(({ file, relativePath }, index) => ({
        entryType: 'file',
        error: '',
        file,
        id: `file-${relativePath}-${file.size}-${file.lastModified}-${index}`,
        progress: 0,
        relativePath,
        status: 'queued',
      })),
    ]);
  }, [open, selection]);

  const queuedItem = useMemo(
    () => queue.find(({ status }) => status === 'queued'),
    [queue],
  );
  const isRunning = currentId !== null || queue.some(({ status }) => status === 'queued');
  const hasCompletedChange = queue.some(({ status }) => status === 'complete');
  const isFinished = queue.length > 0 && queue.every(({ status }) => terminalStates.has(status));

  useEffect(() => {
    if (!open || currentId || !queuedItem) return;

    const parents = new Set(parentFolderPaths(queuedItem.relativePath));
    const failedParent = queue.find((item) => (
      item.entryType === 'folder'
      && parents.has(item.relativePath)
      && (item.status === 'cancelled' || item.status === 'failed')
    ));
    if (failedParent) {
      setQueue((items) => items.map((item) => (
        item.id === queuedItem.id
          ? {
              ...item,
              blockedBy: failedParent.id,
              error: t('library.folders.manager.upload-dialog.parent-folder-failed'),
              status: 'failed',
            }
          : item
      )));
      return;
    }

    const controller = new AbortController();
    abortController.current = controller;
    setCurrentId(queuedItem.id);
    setQueue((items) => items.map((item) => (
      item.id === queuedItem.id
        ? { ...item, error: '', progress: 0, status: 'uploading' }
        : item
    )));

    const { name, parent } = parentAndName(queuedItem.relativePath);
    const operation = queuedItem.entryType === 'folder'
      ? createLibraryFolder(
          joinLibraryPath(folder, parent),
          name,
          { signal: controller.signal },
        )
      : uploadLibraryFile({
          file: queuedItem.file,
          folder: joinLibraryPath(folder, parent),
          signal: controller.signal,
          onProgress: (progress) => {
            setQueue((items) => items.map((item) => (
              item.id === queuedItem.id ? { ...item, progress } : item
            )));
          },
        });

    operation
      .then(() => {
        setQueue((items) => items.map((item) => (
          item.id === queuedItem.id
            ? { ...item, progress: 100, status: 'complete' }
            : item
        )));
      })
      .catch((error) => {
        const operationError = error.name === 'AbortError'
          ? { code: 'cancelled', message: 'Upload cancelled.' }
          : error;
        setQueue((items) => items.map((item) => (
          item.id === queuedItem.id
            ? {
                ...item,
                blockedBy: undefined,
                error: translateLibraryError(t, operationError),
                status: operationError.code === 'cancelled' ? 'cancelled' : 'failed',
              }
            : item
        )));
      })
      .finally(() => {
        abortController.current = null;
        setCurrentId(null);
      });
  }, [currentId, folder, open, queue, queuedItem, t]);

  useEffect(() => {
    if (
      !open
      || !isFinished
      || !hasCompletedChange
      || refreshedBatch.current === batchNumber.current
    ) {
      return;
    }

    refreshedBatch.current = batchNumber.current;
    refreshLibrary()
      .then(onLibraryChanged)
      .catch((error) => {
        setRefreshError(translateLibraryError(t, error));
        onLibraryChanged();
      });
  }, [hasCompletedChange, isFinished, onLibraryChanged, open, t]);

  const cancelItem = (id) => {
    if (id === currentId) {
      abortController.current?.abort();
      return;
    }
    setQueue((items) => items.map((item) => (
      item.id === id ? { ...item, status: 'cancelled' } : item
    )));
  };

  const cancelAll = () => {
    abortController.current?.abort();
    setQueue((items) => items.map((item) => (
      item.status === 'queued' ? { ...item, status: 'cancelled' } : item
    )));
  };

  const retryItem = (id) => {
    refreshedBatch.current = -1;
    setQueue((items) => items.map((item) => (
      item.id === id || item.blockedBy === id
        ? {
            ...item,
            blockedBy: undefined,
            error: '',
            progress: 0,
            status: 'queued',
          }
        : item
    )));
  };

  const statusText = (item) => {
    if (item.status === 'uploading') {
      if (item.entryType === 'folder') {
        return t('library.folders.manager.upload-dialog.creating-folder');
      }
      return t('library.folders.manager.upload-dialog.uploading', { progress: item.progress });
    }
    if (item.status === 'complete' && item.entryType === 'folder') {
      return t('library.folders.manager.upload-dialog.folder-created');
    }
    if (item.status === 'failed') return item.error;
    return t(`library.folders.manager.upload-dialog.status.${item.status}`);
  };

  return (
    <Dialog fullWidth maxWidth="sm" open={open}>
      <DialogTitle>{t('library.folders.manager.upload-dialog.title')}</DialogTitle>
      <DialogContent>
        {refreshError &&
          <Alert severity="warning" sx={{ marginBottom: 2 }}>
            {refreshError}
          </Alert>
        }
        <List disablePadding>
          {queue.map((item) =>
            <ListItem
              divider
              key={item.id}
              secondaryAction={
                item.status === 'uploading' || item.status === 'queued'
                  ? <Tooltip title={t('library.folders.manager.upload-dialog.cancel-item')}>
                      <IconButton
                        aria-label={t('library.folders.manager.upload-dialog.cancel-item')}
                        edge="end"
                        onClick={() => cancelItem(item.id)}
                        sx={{ height: 44, width: 44 }}
                      >
                        <CancelIcon />
                      </IconButton>
                    </Tooltip>
                  : item.status === 'failed' || item.status === 'cancelled'
                    ? <Tooltip title={t('library.folders.manager.upload-dialog.retry-item')}>
                        <IconButton
                          aria-label={t('library.folders.manager.upload-dialog.retry-item')}
                          edge="end"
                          onClick={() => retryItem(item.id)}
                          sx={{ height: 44, width: 44 }}
                        >
                          <ReplayIcon />
                        </IconButton>
                      </Tooltip>
                    : <CheckCircleIcon color="success" />
              }
              sx={{ paddingRight: 7 }}
            >
              <ListItemText
                primary={item.relativePath}
                secondary={
                  <Box sx={{ minWidth: 0 }}>
                    <Typography
                      color={item.status === 'failed' ? 'error' : 'text.secondary'}
                      component="span"
                      sx={{ overflowWrap: 'anywhere' }}
                      variant="body2"
                    >
                      {item.status === 'failed' && <ErrorIcon fontSize="inherit" sx={{ marginRight: 0.5 }} />}
                      {statusText(item)}
                    </Typography>
                    {item.entryType === 'file' &&
                      (item.status === 'uploading' || item.status === 'queued') &&
                      <LinearProgress
                        aria-label={t('library.folders.manager.upload-dialog.progress', {
                          name: item.relativePath,
                        })}
                        sx={{ marginTop: 0.75 }}
                        value={item.progress}
                        variant="determinate"
                      />
                    }
                  </Box>
                }
                slotProps={{
                  primary: {
                    noWrap: true,
                    title: item.relativePath,
                  },
                  secondary: {
                    component: 'div',
                  },
                }}
              />
            </ListItem>
          )}
        </List>
      </DialogContent>
      <DialogActions>
        {isRunning &&
          <Button color="error" onClick={cancelAll} sx={{ minHeight: 44 }}>
            {t('library.folders.manager.upload-dialog.cancel-all')}
          </Button>
        }
        <Button
          disabled={isRunning}
          onClick={onClose}
          sx={{ minHeight: 44 }}
          variant="contained"
        >
          {t('general.buttons.close')}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default UploadDialog;
