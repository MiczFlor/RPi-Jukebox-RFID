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


const RepeatOptions = ({
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
          {t('cards.controls.actions.audio.repeat.description')}
        </Typography>
        <FormControl component="fieldset">
          <RadioGroup
            aria-label="gender"
            name="audio_repeat_options"
            value={option || 'toggle'}
            onChange={onChange}
          >
            <FormControlLabel
              control={<Radio />}
              label={t('cards.controls.actions.audio.repeat.label-toggle')}
              value="toggle"
            />
            <FormControlLabel
              control={<Radio />}
              label={t('cards.controls.actions.audio.repeat.label-toggle-repeat')}
              value="toggle_repeat"
            />
            <FormControlLabel
              control={<Radio />}
              label={t('cards.controls.actions.audio.repeat.label-toggle-repeat-single')}
              value="toggle_repeat_single"
            />
            <FormControlLabel
              control={<Radio />}
              label={t('cards.controls.actions.audio.repeat.label-enable-repeat')}
              value="enable_repeat"
            />
            <FormControlLabel
              control={<Radio />}
              label={t('cards.controls.actions.audio.repeat.label-enable-repeat-single')}
              value="enable_repeat_single"
            />
            <FormControlLabel
              control={<Radio />}
              label={t('cards.controls.actions.audio.repeat.label-disable')}
              value="disable"
            />
          </RadioGroup>
        </FormControl>
      </Grid>
    </Grid>
  );
};

export default RepeatOptions;
