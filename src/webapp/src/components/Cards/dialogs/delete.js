import React from 'react';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';

const CardsDeleteDialog = ({ open, onClose, doDelete, cardId }) => (
  <Dialog
    open={open}
    onClose={onClose}
    aria-labelledby="alert-dialog-title"
    aria-describedby="alert-dialog-description"
  >
    <DialogTitle id="alert-dialog-title">
      {`Delete Card '${cardId}'`}
    </DialogTitle>
    <DialogContent>
      <DialogContentText id="alert-dialog-description">
        Are you sure you want to delete this card?
      </DialogContentText>
    </DialogContent>
    <DialogActions>
      <Button onClick={onClose} color="primary" autoFocus>
        Cancel
      </Button>
      <Button onClick={doDelete} color="secondary">
        Delete
      </Button>
    </DialogActions>
  </Dialog>
);

export default CardsDeleteDialog;
