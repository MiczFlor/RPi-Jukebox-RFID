import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';

import {
  Alert,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  TextField,
} from '@mui/material';

import {
  createLibraryFolder,
  translateLibraryError,
} from '../../../../utils/library-api';

const CreateFolderDialog = ({
  folder,
  onClose,
  onCreated,
  open,
}) => {
  const { t } = useTranslation();
  const [name, setName] = useState('');
  const [error, setError] = useState('');
  const [isSaving, setIsSaving] = useState(false);

  const close = () => {
    if (isSaving) return;
    setName('');
    setError('');
    onClose();
  };

  const createFolder = async (event) => {
    event.preventDefault();
    const trimmedName = name.trim();
    if (!trimmedName) return;

    setError('');
    setIsSaving(true);
    let created = false;
    try {
      await createLibraryFolder(folder, trimmedName);
      setName('');
      created = true;
    }
    catch (requestError) {
      setError(translateLibraryError(t, requestError));
    }
    finally {
      setIsSaving(false);
    }
    if (created) onCreated();
  };

  return (
    <Dialog fullWidth maxWidth="xs" onClose={close} open={open}>
      <form onSubmit={createFolder}>
        <DialogTitle>{t('library.folders.manager.create.title')}</DialogTitle>
        <DialogContent>
          {error && <Alert severity="error" sx={{ marginBottom: 2 }}>{error}</Alert>}
          <TextField
            autoFocus
            disabled={isSaving}
            fullWidth
            inputProps={{ maxLength: 255 }}
            label={t('library.folders.manager.create.name')}
            margin="dense"
            onChange={(event) => setName(event.target.value)}
            required
            value={name}
          />
        </DialogContent>
        <DialogActions>
          <Button disabled={isSaving} onClick={close} sx={{ minHeight: 44 }}>
            {t('general.buttons.cancel')}
          </Button>
          <Button
            disabled={isSaving || !name.trim()}
            sx={{ minHeight: 44 }}
            type="submit"
            variant="contained"
          >
            {t('library.folders.manager.create.confirm')}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default CreateFolderDialog;
