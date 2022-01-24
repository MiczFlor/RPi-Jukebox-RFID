import React from 'react';
import { isEmpty } from 'ramda';
import { useTranslation } from 'react-i18next';

import {
  FormControl,
  Grid,
  NativeSelect,
  Typography,
} from '@mui/material';

import { JUKEBOX_ACTIONS_MAP } from '../../../config';
import { getActionAndCommand } from '../utils';

const CommandSelector = ({
  actionData,
  handleActionDataChange,
}) => {
  const { t } = useTranslation();
  const { action, command = {} } = getActionAndCommand(actionData);
  const commandList = Object.keys(JUKEBOX_ACTIONS_MAP[action].commands);
  const value = isEmpty(command) ? 0 : command;

  const onChange = (event) => {
    handleActionDataChange(action, event.target?.value);
  }

  return (
    <Grid container direction="row" alignItems="center">
      <Grid item xs={5}>
        <Typography>
          {t('cards.controls.command-selector.title')}
        </Typography>
      </Grid>
      <Grid item xs={7}>
        <FormControl>
          <NativeSelect
            value={value}
            onChange={onChange}
            name="commands"
            inputProps={{
              'aria-label': t(
                'cards.controls.command-selector.label',
                { title: JUKEBOX_ACTIONS_MAP[action]?.title }
              )
            }}
          >
            {commandList.length &&
              <option key={0} value={'0'} disabled={true}>
                {t('cards.controls.command-selector.placeholder')}
              </option>
            }
            {commandList.map((command, key) =>
              <option
                key={key}
                value={commandList[key]}
              >
                {t(`cards.controls.command-selector.commands.${command}`)}
              </option>
            )}
          </NativeSelect>
        </FormControl>
      </Grid>
    </Grid>
  );
};

export default CommandSelector;