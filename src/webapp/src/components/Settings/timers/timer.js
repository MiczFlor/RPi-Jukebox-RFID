import React, { useCallback, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import {
  Box,
  Grid,
  Switch,
  Typography,
} from '@mui/material';
import { useTheme } from '@mui/material/styles';

import request from '../../../utils/request';
import {
  Countdown,
  SliderTimer
} from '../../general';

const Timer = ({ type }) => {
  const { t } = useTranslation();
  const theme = useTheme();

  // Constants
  const pluginName = `timer_${type.replace('-', '_')}`;

  // State
  const [error, setError] = useState(null);
  const [enabled, setEnabled] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [status, setStatus] = useState({ enabled: false });
  const [waitSeconds, setWaitSeconds] = useState(0);

  // Requests
  const cancelTimer = async () => {
    await request(`${pluginName}.cancel`);
    setStatus({ enabled: false });
  };

  const setTimer = async (event, wait_seconds) => {
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
    setWaitSeconds(timerStatus?.wait_seconds || 0);
  }, [pluginName]);


  // Event Handlers
  const handleSwitch = (event) => {
    setEnabled(event.target.checked);
    setWaitSeconds(0); // Always start the slider at 0
    cancelTimer();
  }

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
          {status?.enabled &&
            <Countdown
              seconds={status.remaining_seconds}
              onEnd={() => setEnabled(false)}
              stringEnded={t('settings.timers.ended')}
            />
          }
          {error &&
            <Typography>⚠️</Typography>
          }
          <Switch
            checked={enabled}
            disabled={isLoading}
            onChange={handleSwitch}
          />
        </Box>
      </Grid>
      {enabled &&
        <Grid item sx={{ padding: theme.spacing(1) }}>
          <SliderTimer
            value={waitSeconds}
            onChangeCommitted={setTimer}
          />
        </Grid>
      }
    </Grid>
  );
};

export default Timer;
