import React from 'react';

import {
  FormControl,
  NativeSelect
} from '@mui/material';

import { JUKEBOX_ACTIONS_MAP } from '../../../config';

const SelectQuickSelects = ({
  selectedAction,
  handleActionChange
}) => {
  return (
    <FormControl>
      <NativeSelect
        value={selectedAction || '0'}
        onChange={handleActionChange}
        name="quick-select-actions"
        inputProps={{ 'aria-label': 'Quick Select Actions' }}
      >
        <option key={0} value={'0'} disabled={true}>Select an action</option>
        {Object.keys(JUKEBOX_ACTIONS_MAP).map((action) =>
          <option
            key={action}
            value={action}
          >
            {JUKEBOX_ACTIONS_MAP[action].title}
          </option>
        )}
      </NativeSelect>
    </FormControl>
  );
};

export default SelectQuickSelects;
