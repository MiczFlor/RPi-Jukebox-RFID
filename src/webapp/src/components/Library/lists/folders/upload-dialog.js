import React, {
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
  refreshLibrary,
  translateLibraryError,
  uploadLibraryFile,
} from '../../../../utils/library-api';

const terminalStates = new Set(['cancelled', 'complete', 'failed']);

const UploadDialog = ({
  files,
  folder,
  onClose,
  onLibraryChanged,
  open,
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
    setQueue(files.map((file, index) => ({
      error: '',
      file,
      id: `${file.name}-${file.size}-${file.lastModified}-${index}`,
      progress: 0,
      status: 'queued',
    })));
  }, [files, open]);

  const queuedItem = useMemo(
    () => queue.find(({ status }) => status === 'queued'),
    [queue],
  );
  const isRunning = currentId !== null || queue.some(({ status }) => status === 'queued');
  const hasCompletedUpload = queue.some(({ status }) => status === 'complete');
  const isFinished = queue.length > 0 && queue.every(({ status }) => terminalStates.has(status));

  useEffect(() => {
    if (!open || currentId || !queuedItem) return;

    const controller = new AbortController();
    abortController.current = controller;
    setCurrentId(queuedItem.id);
    setQueue((items) => items.map((item) => (
      item.id === queuedItem.id
        ? { ...item, error: '', progress: 0, status: 'uploading' }
        : item
    )));

    uploadLibraryFile({
      file: queuedItem.file,
      folder,
      signal: controller.signal,
      onProgress: (progress) => {
        setQueue((items) => items.map((item) => (
          item.id === queuedItem.id ? { ...item, progress } : item
        )));
      },
    })
      .then(() => {
        setQueue((items) => items.map((item) => (
          item.id === queuedItem.id
            ? { ...item, progress: 100, status: 'complete' }
            : item
        )));
      })
      .catch((error) => {
        setQueue((items) => items.map((item) => (
          item.id === queuedItem.id
            ? {
                ...item,
                error: translateLibraryError(t, error),
                status: error.code === 'cancelled' ? 'cancelled' : 'failed',
              }
            : item
        )));
      })
      .finally(() => {
        abortController.current = null;
        setCurrentId(null);
      });
  }, [currentId, folder, open, queuedItem, t]);

  useEffect(() => {
    if (
      !open
      || !isFinished
      || !hasCompletedUpload
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
  }, [hasCompletedUpload, isFinished, onLibraryChanged, open, t]);

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
      item.id === id
        ? { ...item, error: '', progress: 0, status: 'queued' }
        : item
    )));
  };

  const statusText = (item) => {
    if (item.status === 'uploading') {
      return t('library.folders.manager.upload-dialog.uploading', { progress: item.progress });
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
                  ? <Tooltip title={t('library.folders.manager.upload-dialog.cancel-file')}>
                      <IconButton
                        aria-label={t('library.folders.manager.upload-dialog.cancel-file')}
                        edge="end"
                        onClick={() => cancelItem(item.id)}
                        sx={{ height: 44, width: 44 }}
                      >
                        <CancelIcon />
                      </IconButton>
                    </Tooltip>
                  : item.status === 'failed' || item.status === 'cancelled'
                    ? <Tooltip title={t('library.folders.manager.upload-dialog.retry-file')}>
                        <IconButton
                          aria-label={t('library.folders.manager.upload-dialog.retry-file')}
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
                primary={item.file.name}
                primaryTypographyProps={{
                  noWrap: true,
                  title: item.file.name,
                }}
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
                    {(item.status === 'uploading' || item.status === 'queued') &&
                      <LinearProgress
                        aria-label={t('library.folders.manager.upload-dialog.progress', {
                          name: item.file.name,
                        })}
                        sx={{ marginTop: 0.75 }}
                        value={item.progress}
                        variant="determinate"
                      />
                    }
                  </Box>
                }
                secondaryTypographyProps={{ component: 'div' }}
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
