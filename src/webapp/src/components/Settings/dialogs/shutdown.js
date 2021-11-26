import React, { useState } from 'react';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import Snackbar from '@mui/material/Snackbar';

import request from '../../../utils/request';

export default function ShutDownDialog() {
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
      await request('shutdown');
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
        onClick={handleClickOpen}>Shut Down</Button>

      <Dialog
        open={dialogOpen}
        onClose={handleCancelShutdown}
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
      >
        <DialogTitle id="alert-dialog-title">
          {!shuttingDown && "Shut Down"}
          {shuttingDown && "👋 Good bye"}
        </DialogTitle>
        <DialogContent>
          {
            !shuttingDown &&
            <DialogContentText id="alert-dialog-description">
              Are you sure you want to shut down your Phoniebox now?
            </DialogContentText>
          }

          {
            shuttingDown &&
            <DialogContentText id="alert-dialog-description">
              The Phoniebox is being shut down!
            </DialogContentText>
          }
        </DialogContent>
        <DialogActions>
          <Button
            color="secondary"
            disabled={shuttingDown}
            onClick={handleCancelShutdown}
          >
            Cancel
          </Button>
          <Button
            autoFocus
            color="primary"
            disabled={shuttingDown}
            onClick={doShutdown}
          >
            Shut Down
          </Button>
        </DialogActions>
      </Dialog>

      <Snackbar
        id="error"
        open={showError}
        autoHideDuration={5000}
        onClose={handleCloseError}
        message="Shut Down failed"
      />
    </>
  );
}
