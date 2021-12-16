import React from 'react';
import { isEmpty } from 'ramda';

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
  const { action, command = {} } = getActionAndCommand(actionData);
  const commandList = Object.keys(JUKEBOX_ACTIONS_MAP[action].commands);
  const value = isEmpty(command) ? 0 : command;

  const onChange = (event) => {
    handleActionDataChange(action, event.target?.value);
  }

  return (
    <Grid container direction="row" alignItems="center">
      <Grid item xs={5}>
        <Typography>Commands</Typography>
      </Grid>
      <Grid item xs={7}>
        <FormControl>
          <NativeSelect
            value={value}
            onChange={onChange}
            name="commands"
            inputProps={{ 'aria-label': `${JUKEBOX_ACTIONS_MAP[action]?.title} commands` }}
          >
            {commandList.length &&
              <option key={0} value={'0'} disabled={true}>
                Select a command
              </option>
            }
            {commandList.map((command, key) =>
              <option
                key={key}
                value={commandList[key]}
              >
                {JUKEBOX_ACTIONS_MAP[action]?.commands[command]?.title}
              </option>
            )}
          </NativeSelect>
        </FormControl>
      </Grid>
    </Grid>
  );
};

export default CommandSelector;