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
} from '../../../../utils';


const ChangeOnRfidScan = ({
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
          {t('cards.controls.actions.synchronisation.rfidcards.description')}
        </Typography>
        <FormControl component="fieldset">
          <RadioGroup
            aria-label="gender"
            name="sync_rfidcards_change_on_rfid_scan"
            value={option || 'toggle'}
            onChange={onChange}
          >
            <FormControlLabel
              control={<Radio />}
              label={t('cards.controls.actions.synchronisation.rfidcards.label-toggle')}
              value="toggle"
            />
            <FormControlLabel
              control={<Radio />}
              label={t('cards.controls.actions.synchronisation.rfidcards.label-enable')}
              value="enable"
            />
            <FormControlLabel
              control={<Radio />}
              label={t('cards.controls.actions.synchronisation.rfidcards.label-disable')}
              value="disable"
            />
          </RadioGroup>
        </FormControl>
      </Grid>
    </Grid>
  );
};

export default ChangeOnRfidScan;
