import { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';

import {
  Alert,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  List,
  ListItem,
  ListItemText,
} from '@mui/material';

import {
  deleteLibraryEntries,
  refreshLibrary,
  translateLibraryError,
} from '../../../../utils/library-api';

const DeleteEntriesDialog = ({
  entries,
  onClose,
  onDeleted,
  open,
}) => {
  const { t } = useTranslation();
  const [error, setError] = useState('');
  const [isDeleting, setIsDeleting] = useState(false);
  const containsFolder = useMemo(
    () => entries.some(({ type }) => type === 'directory'),
    [entries],
  );

  const close = () => {
    if (isDeleting) return;
    setError('');
    onClose();
  };

  const deleteEntries = async () => {
    setError('');
    setIsDeleting(true);
    try {
      await deleteLibraryEntries(entries.map(({ relpath }) => relpath));
    }
    catch (requestError) {
      setError(translateLibraryError(t, requestError));
      setIsDeleting(false);
      return;
    }

    let refreshWarning = '';
    try {
      await refreshLibrary();
    }
    catch (requestError) {
      refreshWarning = translateLibraryError(t, requestError);
    }
    setIsDeleting(false);
    onDeleted(refreshWarning);
  };

  return (
    <Dialog fullWidth maxWidth="sm" onClose={close} open={open}>
      <DialogTitle>
        {t('library.folders.manager.delete.title', { count: entries.length })}
      </DialogTitle>
      <DialogContent>
        {error && <Alert severity="error" sx={{ marginBottom: 2 }}>{error}</Alert>}
        <DialogContentText>
          {t('library.folders.manager.delete.permanent')}
        </DialogContentText>
        {containsFolder &&
          <Alert severity="warning" sx={{ marginTop: 2 }}>
            {t('library.folders.manager.delete.folder-warning')}
          </Alert>
        }
        <List dense sx={{ maxHeight: 240, overflowY: 'auto' }}>
          {entries.map(({ name, relpath }) =>
            <ListItem disableGutters key={relpath}>
              <ListItemText
                primary={name}
                secondary={relpath === name ? undefined : relpath}
              />
            </ListItem>
          )}
        </List>
      </DialogContent>
      <DialogActions>
        <Button disabled={isDeleting} onClick={close} sx={{ minHeight: 44 }}>
          {t('general.buttons.cancel')}
        </Button>
        <Button
          color="error"
          disabled={isDeleting}
          onClick={deleteEntries}
          sx={{ minHeight: 44 }}
          variant="contained"
        >
          {t('general.buttons.delete')}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default DeleteEntriesDialog;
