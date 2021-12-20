import React from 'react';
import { isEmpty } from 'ramda';

import {
  FormControl,
  NativeSelect
} from '@mui/material';

import { JUKEBOX_ACTIONS_MAP } from '../../../config';
import { getActionAndCommand } from '../utils';

const SelectCommandAliases = ({
  actionData,
  handleActionChange
}) => {
  const { action = {} } = getActionAndCommand(actionData);
  const actionsList = Object.keys(JUKEBOX_ACTIONS_MAP);
  const value = isEmpty(action) ? 0 : action;

  return (
    <FormControl>
      <NativeSelect
        value={value}
        onChange={handleActionChange}
        name="quick-select-actions"
        inputProps={{ 'aria-label': 'Actions' }}
      >
        <option key={0} value={'0'} disabled={true}>Select an action</option>
        {actionsList.map((action, key) =>
          <option
            key={key}
            value={actionsList[key]}
          >
            {JUKEBOX_ACTIONS_MAP[action].title}
          </option>
        )}
      </NativeSelect>
    </FormControl>
  );
};

export default SelectCommandAliases;
