import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';

import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import Snackbar from '@mui/material/Snackbar';

import request from '../../../utils/request';

export default function ShutDownDialog() {
  const { t } = useTranslation();

  const [dialogOpen, setDialogOpen] = useState(false);
  const [shuttingDown, setShuttingDown] = useState(false);
  const [showError, setShowError] = useState(false);

  const handleClickOpen = () => {
    setDialogOpen(true);
  };

  const handleCancelShutdown = () => {
    setDialogOpen(false);
  };

  const doShutdown = async () => {
    try {
      setShuttingDown(true);
      request('shutdown');
    }
    catch(error) {
      setShuttingDown(false);
      setDialogOpen(false);
      setShowError(true);
    }
  };

  const handleCloseError = () => {
    setShowError(false);
  };

  return (
    <>
      <Button
        variant="outlined"
        onClick={handleClickOpen}
      >
        {t('settings.dialogs.shutdown.button-title')}
      </Button>
      <Dialog
        open={dialogOpen}
        onClose={handleCancelShutdown}
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
      >
        <DialogTitle id="alert-dialog-title">
          {!shuttingDown && t('settings.dialogs.shutdown.title')}
          {shuttingDown && t('settings.dialogs.reboot.bye')}
        </DialogTitle>
        <DialogContent>
          {
            !shuttingDown &&
            <DialogContentText id="alert-dialog-description">
              {t('settings.dialogs.shutdown.description-confirm')}
            </DialogContentText>
          }

          {
            shuttingDown &&
            <DialogContentText id="alert-dialog-description">
              {t('settings.dialogs.shutdown.description-success')}
            </DialogContentText>
          }
        </DialogContent>
        <DialogActions>
          <Button
            color="secondary"
            disabled={shuttingDown}
            onClick={handleCancelShutdown}
          >
            {t('general.buttons.cancel')}
          </Button>
          <Button
            autoFocus
            color="primary"
            disabled={shuttingDown}
            onClick={doShutdown}
          >
            {t('settings.dialogs.shutdown.button-title')}
          </Button>
        </DialogActions>
      </Dialog>

      <Snackbar
        id="error"
        open={showError}
        autoHideDuration={5000}
        onClose={handleCloseError}
        message={t('settings.dialogs.shutdown.failed')}
      />
    </>
  );
}
