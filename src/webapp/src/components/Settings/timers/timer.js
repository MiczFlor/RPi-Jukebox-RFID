import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import {
  Box,
  Grid,
  Slider,
  Switch,
  Typography,
} from '@mui/material';
import { useTheme } from '@mui/material/styles';

import request from '../../../utils/request';
import Countdown from './countdown';
import { TIMER_STEPS } from '../../../config';

const Timer = ({ type }) => {
  const { t } = useTranslation();
  const theme = useTheme();

  // Constants
  const pluginName = `timer_${type.replace('-', '_')}`;
  const marks = TIMER_STEPS.map((value, index) => (
    { label: value, value: index }
  ));
  const valueLabelFormat = (value) => {
    if (value === 0) return t('settings.timers.option-label-off');
    return t('settings.timers.option-label-timeslot', { value });
  }

  // State
  const [error, setError] = useState(null);
  const [enabled, setEnabled] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [status, setStatus] = useState({ enabled: false });
  const [step, setStep] = useState(0);

  // Requests
  const cancelTimer = async () => {
    await request(`timers.${pluginName}.cancel`);
    setStatus({ enabled: false });
  };

  const setTimer = async (event, step) => {
    const seconds = TIMER_STEPS[step] * 60;

    await cancelTimer();

    if (step > 0) {
      await request(
        `timers.${pluginName}.start`,
        { wait_seconds: seconds }
      );
      await fetchTimerStatus();
    }
  }

  const fetchTimerStatus = async () => {
    if (!enabled) setIsLoading(true);

    const {
      result: timerStatus,
      error: timerStatusError
    } = await request(`timers.${pluginName}.get_state`);

    if(timerStatusError) {
      setEnabled(false);
      return setError(timerStatusError);
    }

    setEnabled(timerStatus?.enabled);
    setStatus(timerStatus);
    setStep(TIMER_STEPS.indexOf(timerStatus.wait_seconds / 60));
    setIsLoading(false);
  }

  // Event Handlers
  const handleSwitch = (event) => {
    setEnabled(event.target.checked);
    setStep(0); // Always start the slider at 0
    cancelTimer();
  }

  const handleSliderChange = (event, step) => {
    setStep(step);
  }

  // Effects
  useEffect(() => {
    fetchTimerStatus();
  }, []);

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
          <Slider
            value={step}
            marks={marks}
            max={TIMER_STEPS.length-1}
            getAriaValueText={valueLabelFormat}
            valueLabelFormat={valueLabelFormat}
            min={0}
            step={1}
            scale={(value) => TIMER_STEPS[value]}
            valueLabelDisplay="auto"
            onChange={handleSliderChange}
            onChangeCommitted={setTimer}
          />
        </Grid>
      }
    </Grid>
  );
};

export default Timer;
