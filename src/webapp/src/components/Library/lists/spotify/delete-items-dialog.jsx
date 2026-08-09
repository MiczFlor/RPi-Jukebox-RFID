import { useEffect, useState } from 'react';
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

const DeleteSpotifyItemsDialog = ({
  items,
  onClose,
  onDelete,
  open,
}) => {
  const { t } = useTranslation();
  const [error, setError] = useState('');
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    if (!open) {
      setError('');
      setIsDeleting(false);
    }
  }, [open]);

  const close = () => {
    if (isDeleting) return;
    setError('');
    onClose();
  };

  const remove = async () => {
    setError('');
    setIsDeleting(true);
    try {
      await onDelete(items);
    }
    catch (requestError) {
      setError(requestError.message);
      setIsDeleting(false);
    }
  };

  return (
    <Dialog fullWidth maxWidth="sm" onClose={close} open={open}>
      <DialogTitle>
        {t('library.spotify.manager.delete.title', { count: items.length })}
      </DialogTitle>
      <DialogContent>
        {error &&
          <Alert severity="error" sx={{ marginBottom: 2 }}>
            {error}
          </Alert>
        }
        <DialogContentText>
          {t('library.spotify.manager.delete.description')}
        </DialogContentText>
        <List dense sx={{ maxHeight: 240, overflowY: 'auto' }}>
          {items.map((item) => (
            <ListItem disableGutters key={item.content_uri}>
              <ListItemText
                primary={item.album}
                secondary={item.albumartist}
              />
            </ListItem>
          ))}
        </List>
      </DialogContent>
      <DialogActions>
        <Button disabled={isDeleting} onClick={close} sx={{ minHeight: 44 }}>
          {t('general.buttons.cancel')}
        </Button>
        <Button
          color="error"
          disabled={isDeleting}
          onClick={remove}
          sx={{ minHeight: 44 }}
          variant="contained"
        >
          {t('general.buttons.delete')}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default DeleteSpotifyItemsDialog;
