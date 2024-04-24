import React, { useCallback, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import {
  Box,
  Grid,
  Typography,
} from '@mui/material';

import request from '../../../utils/request';
import { Countdown } from '../../general';
import SetTimerDialog from './set-timer-dialog';

const Timer = ({ type }) => {
  const { t } = useTranslation();

  // Constants
  const pluginName = `timer_${type.replace('-', '_')}`;

  // State
  const [error, setError] = useState(null);
  const [enabled, setEnabled] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [status, setStatus] = useState({ enabled: false });
  const [waitSeconds, setWaitSeconds] = useState(0);
  const [running, setRunning] = useState(true);

  // Requests
  const cancelTimer = async () => {
    await request(`${pluginName}.cancel`);
    setEnabled(false);
  };

  const setTimer = async (wait_seconds) => {
    await cancelTimer();

    if (wait_seconds > 0) {
      await request(pluginName, { wait_seconds } );
      fetchTimerStatus();
    }
  }

  const fetchTimerStatus = useCallback(async () => {
    const {
      result: timerStatus,
      error: timerStatusError
    } = await request(`${pluginName}.get_state`);

    if(timerStatusError) {
      setEnabled(false);
      return setError(timerStatusError);
    }

    setStatus(timerStatus);
    setEnabled(timerStatus?.enabled);
    if (timerStatus.running === undefined) {
      setRunning(true);
    }
    else {
      setRunning(timerStatus.running);
    }
  }, [pluginName]);

  // Effects
  useEffect(() => {
    fetchTimerStatus();
    setIsLoading(false);
  }, [fetchTimerStatus]);

  return (
    <Grid container direction="column" justifyContent="center">
      <Grid container direction="row" justifyContent="space-between" alignItems="center">
        <Typography>
          {t(`settings.timers.${type}`)}
        </Typography>
        <Box sx={{
          display: 'flex',
          alignItems: 'center',
          marginLeft: '0',
        }}>
          {enabled && running &&
            <Countdown
              seconds={status.remaining_seconds}
              onEnd={() => setEnabled(false)}
              stringEnded={t('settings.timers.ended')}
            />
          }
          {enabled && !running &&
            <Typography>
              Paused
            </Typography>
          }
          {error &&
            <Typography>⚠️</Typography>
          }
          {!isLoading &&
            <SetTimerDialog
              type={type}
              enabled={enabled}
              setTimer={setTimer}
              cancelTimer={cancelTimer}
              waitSeconds={waitSeconds}
              setWaitSeconds={setWaitSeconds}
            />
          }
        </Box>
      </Grid>
    </Grid>
  );
};

export default Timer;
