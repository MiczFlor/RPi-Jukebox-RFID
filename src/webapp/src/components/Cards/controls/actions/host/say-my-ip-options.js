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


const SayMyIpOptions = ({
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
          {t('cards.controls.actions.host.description')}
        </Typography>
        <FormControl component="fieldset">
          <RadioGroup
            aria-label="gender"
            name="say-my-name"
            value={option || 'full'}
            onChange={onChange}
          >
            <FormControlLabel
              control={<Radio />}
              label={t('cards.controls.actions.host.label-full')}
              value="full"
            />
            <FormControlLabel
              control={<Radio />}
              label={t('cards.controls.actions.host.label-short')}
              value="short"
            />
          </RadioGroup>
        </FormControl>
      </Grid>
    </Grid>
  );
};

export default SayMyIpOptions;
