import React from 'react';
import { useTranslation } from 'react-i18next';

import {
  Grid,
  Typography,
} from '@mui/material';

import {
  getActionAndCommand,
  getArgsValues,
} from '../../../utils';
import { SliderTimer } from '../../../../general';

const SliderSetTimer = ({
  actionData,
  handleActionDataChange,
}) => {
  const { t } = useTranslation();

  const { action, command } = getActionAndCommand(actionData);
  const [wait_seconds] = getArgsValues(actionData);

  const onChangeCommitted = (event, wait_seconds) => {
    handleActionDataChange(action, command, { wait_seconds })
  };

  return (
    <Grid container alignItems="center" sx={{ marginTop: '20px' }}>
      <Grid item xs={12}>
        <Typography>
          {t('cards.controls.actions.timers.description')}
        </Typography>
        <SliderTimer
          value={wait_seconds || 0}
          onChangeCommitted={onChangeCommitted}
        />
      </Grid>
    </Grid>
  );
};

export default SliderSetTimer;
