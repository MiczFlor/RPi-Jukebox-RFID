import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';

import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Grid,
} from '@mui/material';
import { useTheme } from '@mui/material/styles';

import {
  SliderTimer
} from '../../general';

export default function SetTimerDialog({
  type,
  enabled,
  setTimer,
  cancelTimer,
  waitSeconds,
  setWaitSeconds,
}) {
  const { t } = useTranslation();
  const theme = useTheme();

  const [dialogOpen, setDialogOpen] = useState(false);

  const handleClickOpen = () => {
    setWaitSeconds(0);
    setDialogOpen(true);
  };

  const handleCancel = () => {
    setDialogOpen(false);
  };

  const handleSetTimer = () => {
    setTimer(waitSeconds)
    setDialogOpen(false);
  }

  return (
    <Box sx={{ marginLeft: '10px' }}>
      {!enabled &&
        <Button
          variant="outlined"
          onClick={handleClickOpen}
        >
          {t('settings.timers.set')}
        </Button>
      }
      {enabled &&
        <Button
          variant="outlined"
          onClick={cancelTimer}
        >
          {t('settings.timers.cancel')}
        </Button>
      }
      <Dialog
        open={dialogOpen}
        onClose={handleCancel}
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
      >
        <DialogTitle id="alert-dialog-title">
          {t('settings.timers.dialog.title', { value: t(`settings.timers.${type}.title`)} )}
        </DialogTitle>
        <DialogContent>
          <DialogContentText id="alert-dialog-description">
            {t('settings.timers.dialog.description')}
          </DialogContentText>
          <Grid item sx={{ padding: theme.spacing(1) }}>
            <SliderTimer
              value={waitSeconds || 0}
              onChangeCommitted={(evt, value) => { setWaitSeconds(value) }}
            />
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCancel} color="secondary">
          {t('settings.timers.dialog.cancel')}
          </Button>
          <Button
            onClick={handleSetTimer}
            color="primary"
            autoFocus
            disabled={waitSeconds === 0}
          >
            {t('settings.timers.dialog.start')}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
