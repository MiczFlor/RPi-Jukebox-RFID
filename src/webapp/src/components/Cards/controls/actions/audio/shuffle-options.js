import React from 'react';
import { useTranslation } from 'react-i18next';

import {
  Grid,
  FormControl,
  FormControlLabel,
  Radio,
  RadioGroup,
  Typography,
} from '@mui/material';

import {
  getActionAndCommand,
  getArgsValues,
} from '../../../utils';


const ShuffleOptions = ({
  actionData,
  handleActionDataChange,
}) => {
  const { t } = useTranslation();

  const { action, command } = getActionAndCommand(actionData);
  const [option] = getArgsValues(actionData);

  const onChange = (event, option) => {
    handleActionDataChange(action, command, { option })
  };

  return (
    <Grid container alignItems="center" sx={{ marginTop: '20px' }}>
      <Grid item xs={12}>
        <Typography>
          {t('cards.controls.actions.audio.shuffle.description')}
        </Typography>
        <FormControl component="fieldset">
          <RadioGroup
            aria-label="gender"
            name="audio_shuffle_options"
            value={option || 'toggle'}
            onChange={onChange}
          >
            <FormControlLabel
              control={<Radio />}
              label={t('cards.controls.actions.audio.shuffle.label-toggle')}
              value="toggle"
            />
            <FormControlLabel
              control={<Radio />}
              label={t('cards.controls.actions.audio.shuffle.label-enable')}
              value="enable"
            />
            <FormControlLabel
              control={<Radio />}
              label={t('cards.controls.actions.audio.shuffle.label-disable')}
              value="disable"
            />
          </RadioGroup>
        </FormControl>
      </Grid>
    </Grid>
  );
};

export default ShuffleOptions;
