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
} from '../utils.js';

const OptionsSelector = ({
  actionType,
  actionData,
  handleActionDataChange,
  optionLabel,
  options,
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
          {t(optionLabel)}
        </Typography>
        <FormControl component="fieldset">
          <RadioGroup
            aria-label={actionType}
            name={`${actionType}_options`}
            value={option || options[0].value}
            onChange={onChange}
          >
            {options.map(({ labelKey, value }) => (
              <FormControlLabel
                key={value}
                control={<Radio />}
                label={t(labelKey)}
                value={value}
              />
            ))}
          </RadioGroup>
        </FormControl>
      </Grid>
    </Grid>
  );
};

export default OptionsSelector;
