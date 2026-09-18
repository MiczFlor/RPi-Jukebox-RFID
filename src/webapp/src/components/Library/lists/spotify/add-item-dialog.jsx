import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import {
  Alert,
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  TextField,
} from '@mui/material';

const AddSpotifyItemDialog = ({
  onAdd,
  onClose,
  open,
}) => {
  const { t } = useTranslation();
  const [error, setError] = useState('');
  const [isAdding, setIsAdding] = useState(false);
  const [link, setLink] = useState('');

  useEffect(() => {
    if (!open) {
      setError('');
      setIsAdding(false);
      setLink('');
    }
  }, [open]);

  const close = () => {
    if (!isAdding) onClose();
  };

  const add = async (event) => {
    event.preventDefault();
    if (!link.trim()) return;
    setError('');
    setIsAdding(true);
    try {
      await onAdd(link.trim());
    }
    catch (requestError) {
      setError(requestError.message);
      setIsAdding(false);
    }
  };

  return (
    <Dialog fullWidth maxWidth="sm" onClose={close} open={open}>
      <Box component="form" onSubmit={add}>
        <DialogTitle>{t('library.spotify.manager.add-dialog.title')}</DialogTitle>
        <DialogContent>
          {error &&
            <Alert severity="error" sx={{ marginBottom: 2 }}>
              {error}
            </Alert>
          }
          <TextField
            autoFocus
            disabled={isAdding}
            fullWidth
            label={t('library.spotify.manager.add-dialog.link')}
            onChange={(event) => setLink(event.target.value)}
            value={link}
          />
        </DialogContent>
        <DialogActions>
          <Button disabled={isAdding} onClick={close} sx={{ minHeight: 44 }}>
            {t('general.buttons.cancel')}
          </Button>
          <Button
            disabled={isAdding || !link.trim()}
            sx={{ minHeight: 44 }}
            type="submit"
            variant="contained"
          >
            {t('library.spotify.manager.add-dialog.confirm')}
          </Button>
        </DialogActions>
      </Box>
    </Dialog>
  );
};

export default AddSpotifyItemDialog;
