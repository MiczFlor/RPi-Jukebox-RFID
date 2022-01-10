import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';

import {
  Button,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Grid,
  Snackbar,
} from '@mui/material';

import request from '../../../utils/request';

export default function RebootDialog() {
  const { t } = useTranslation();

  const [dialogOpen, setDialogOpen] = useState(false);
  const [waitingForReboot, setWaitingForReboot] = React.useState(false);
  const [showError, setShowError] = useState(false);

  const checkIfBackendIsAvailable = () => {
    const checkingInterval = setInterval(async () => {
      try {
        await request('playerstatus');
        setDialogOpen(false);
        setWaitingForReboot(false);
        clearInterval(checkingInterval);
      }
      catch(error) {
        setWaitingForReboot(true);
        console.log('waiting for reboot');
      }
    }, 15000);
  }

  const handleClickOpen = () => {
    setDialogOpen(true);
  };

  const handleCancelReboot = () => {
    setDialogOpen(false);
  };

  const doReboot = async () => {
    try {
      setWaitingForReboot(true);
      checkIfBackendIsAvailable();
      request('reboot');
    }
    catch(error) {
      setWaitingForReboot(false);
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
        {t('settings.dialogs.reboot.button-title')}
      </Button>
      <Dialog
        open={dialogOpen}
        onClose={handleCancelReboot}
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
      >
        <DialogTitle id="alert-dialog-title">
          {!waitingForReboot && t('settings.dialogs.reboot.title')}
          {waitingForReboot && t('settings.dialogs.reboot.rebooting')}
        </DialogTitle>
        <DialogContent>
          {
            !waitingForReboot &&
            <DialogContentText id="alert-dialog-description">
              {t('settings.dialogs.reboot.description-confirm')}
            </DialogContentText>
          }

          {
            waitingForReboot &&
            <Grid container spacing={2}>
              <Grid item xs={12} justifyContent="center">
                <CircularProgress />
              </Grid>
            </Grid>
          }

        </DialogContent>
        <DialogActions>
          <Button onClick={handleCancelReboot} color="secondary">
            {t('general.buttons.cancel')}
          </Button>
          <Button onClick={doReboot} color="primary" autoFocus>
            {t('settings.dialogs.reboot.button-title')}
          </Button>
        </DialogActions>
      </Dialog>

      <Snackbar
        id="error"
        open={showError}
        autoHideDuration={5000}
        onClose={handleCloseError}
        message={t('settings.dialogs.reboot.failed')}
      />
    </>
  );
}
