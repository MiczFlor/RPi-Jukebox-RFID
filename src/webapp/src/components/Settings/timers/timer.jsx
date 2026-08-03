import {
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
} from 'react';
import { useTranslation } from 'react-i18next';
import { Box, ListItem, ListItemText, Typography } from '@mui/material';
import { Countdown } from '../../general';
import PubSubContext from '../../../context/pubsub/context';
import SetTimerDialog from './set-timer-dialog';
import request from '../../../utils/request';

// Custom hook to manage timer state and logic
const useTimer = (type) => {
  const pluginName = `timer_${type.replace('-', '_')}`;
  const topic = `timers.${pluginName}`;
  const { state: publisherState = {} } = useContext(PubSubContext);
  const publishedStatus = publisherState[topic];
  const publisherVersion = useRef(0);
  const hasPublishedState = useRef(false);
  const [timerState, setTimerState] = useState({
    error: null,
    enabled: false,
    isLoading: true,
    status: { enabled: false },
    waitSeconds: 0,
    running: true,
    revision: 0,
  });

  const applyTimerStatus = useCallback((timerStatus) => {
    setTimerState(prev => ({
      ...prev,
      status: timerStatus,
      enabled: timerStatus?.enabled ?? false,
      running: timerStatus?.running ?? true,
      error: null,
      isLoading: false,
      revision: prev.revision + 1,
    }));
  }, []);

  const fetchTimerStatus = useCallback(async () => {
    const requestedAtVersion = publisherVersion.current;
    const { result: timerStatus, error } = await request(
      `${pluginName}.get_state`,
    );
    if (error) {
      setTimerState(prev => ({
        ...prev,
        error,
        isLoading: false,
      }));
      return;
    }
    if (publisherVersion.current === requestedAtVersion) {
      applyTimerStatus(timerStatus);
    }
  }, [applyTimerStatus, pluginName]);

  const cancelTimer = async () => {
    const { error } = await request(`${pluginName}.cancel`);
    if (error) {
      setTimerState(prev => ({ ...prev, error }));
      return;
    }
    await fetchTimerStatus();
  };

  const setTimer = async (wait_seconds) => {
    if (wait_seconds <= 0) {
      return;
    }
    const { error } = await request(pluginName, { wait_seconds });
    if (error) {
      setTimerState(prev => ({ ...prev, error }));
      return;
    }
    await fetchTimerStatus();
  };

  const setWaitSeconds = (seconds) => {
    setTimerState(prev => ({ ...prev, waitSeconds: seconds }));
  };

  useEffect(() => {
    fetchTimerStatus();
  }, [fetchTimerStatus]);

  useEffect(() => {
    if (publishedStatus !== undefined) {
      hasPublishedState.current = true;
      publisherVersion.current += 1;
      applyTimerStatus(publishedStatus);
    }
    else if (hasPublishedState.current) {
      fetchTimerStatus();
    }
  }, [applyTimerStatus, fetchTimerStatus, publishedStatus]);

  return {
    ...timerState,
    setTimer,
    cancelTimer,
    setWaitSeconds
  };
};

// Separate component for timer actions
const TimerActions = ({ enabled, running, status, revision, error, isLoading, type, onSetTimer, onCancelTimer, waitSeconds, onSetWaitSeconds }) => {
  const { t } = useTranslation();

  return (
    <Box sx={{ alignItems: 'center', display: 'flex', flexShrink: 0 }}>
      {enabled && running && (
        <Countdown
          seconds={status.remaining_seconds}
          resetKey={revision}
          stringEnded={t('settings.timers.ended')}
        />
      )}
      {enabled && !running && (
        <Typography>{t('settings.timers.paused')}</Typography>
      )}
      {error && <Typography>⚠️</Typography>}
      {!isLoading && (
        <SetTimerDialog
          type={type}
          enabled={enabled}
          setTimer={onSetTimer}
          cancelTimer={onCancelTimer}
          waitSeconds={waitSeconds}
          setWaitSeconds={onSetWaitSeconds}
        />
      )}
    </Box>
  );
};

const Timer = ({ type }) => {
  const { t } = useTranslation();
  const timer = useTimer(type);

  return (
    <ListItem
      disableGutters
      sx={{ alignItems: 'center', gap: 2 }}
    >
      <ListItemText
        primary={t(`settings.timers.${type}.title`)}
        secondary={t(`settings.timers.${type}.label`)}
        sx={{ minWidth: 0 }}
      />
      <TimerActions
        {...timer}
        onSetTimer={timer.setTimer}
        onCancelTimer={timer.cancelTimer}
        onSetWaitSeconds={timer.setWaitSeconds}
        type={type}
      />
    </ListItem>
  );
};

export default Timer;

export {
  TimerActions,
  useTimer,
};
