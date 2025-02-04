import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Card,
  CardContent,
  CardHeader,
  Divider,
  FormControlLabel,
  Grid,
  Radio,
  RadioGroup,
} from '@mui/material';
import request from '../../utils/request';

const SettingsSecondSwipe = () => {
  const { t } = useTranslation();
  const [secondSwipeAction, setSecondSwipeAction] = useState('None');
  const [isLoading, setIsLoading] = useState(true);

  const getSecondSwipeStatus = async () => {
    const { result, error } = await request('getSecondSwipeAction');
    if (result && result !== 'error') setSecondSwipeAction(result);
    if ((result && result === 'error') || error) console.error(error);
  };

  const setSecondSwipeStatus = async (action) => {
    setIsLoading(true);
    const { result, error } = await request('setSecondSwipeAction', {
      action: action
    });

    if (error || result === 'error') {
      console.error('An error occurred while setting second swipe status');
      await getSecondSwipeStatus(); // Revert to previous state
    } else {
      setSecondSwipeAction(action);
    }
    setIsLoading(false);
  };

  useEffect(() => {
    const fetchSecondSwipeStatus = async () => {
      setIsLoading(true);
      await getSecondSwipeStatus();
      setIsLoading(false);
    };
    fetchSecondSwipeStatus();
  }, []);

  const handleChange = (event) => {
    setSecondSwipeStatus(event.target.value);
  };

  return (
    <Card>
      <CardHeader
        title={t('settings.secondswipe.title')}
      />
      <Divider />
      <CardContent>
        <Grid container direction="column">
          <Grid item>
            <RadioGroup
              aria-label="second-swipe-action"
              name="action"
              value={secondSwipeAction || ''}
              onChange={handleChange}
            >
              <FormControlLabel
                value="toggle"
                control={<Radio disabled={isLoading} />}
                label={t('settings.secondswipe.toggle')}
              />
              <FormControlLabel
                value="rewind"
                control={<Radio disabled={isLoading} />}
                label={t('settings.secondswipe.rewind')}
              />
              <FormControlLabel
                value="next"
                control={<Radio disabled={isLoading} />}
                label={t('settings.secondswipe.next')}
              />
              <FormControlLabel
                value="None"
                control={<Radio disabled={isLoading} />}
                label={t('settings.secondswipe.none')}
              />
            </RadioGroup>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};

export default SettingsSecondSwipe;
