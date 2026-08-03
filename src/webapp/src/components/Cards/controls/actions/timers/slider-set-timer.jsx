import { useTranslation } from 'react-i18next';

import {
  Checkbox,
  FormControlLabel,
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
  const [wait_seconds, restart = true] = getArgsValues(actionData);

  const onChangeCommitted = (event, wait_seconds) => {
    handleActionDataChange(action, command, { wait_seconds, restart })
  };

  const onRestartChange = (event) => {
    handleActionDataChange(action, command, {
      wait_seconds,
      restart: event.target.checked,
    });
  };

  return (
    <Grid
      container
      sx={{
        alignItems: 'center',
        marginTop: '20px',
      }}
    >
      <Grid size={12}>
        <Typography>
          {t('cards.controls.actions.timers.description')}
        </Typography>
        <SliderTimer
          value={wait_seconds || 0}
          onChangeCommitted={onChangeCommitted}
        />
        <FormControlLabel
          control={
            <Checkbox
              checked={restart}
              onChange={onRestartChange}
            />
          }
          label={t('cards.controls.actions.timers.restart')}
        />
      </Grid>
    </Grid>
  );
};

export default SliderSetTimer;
