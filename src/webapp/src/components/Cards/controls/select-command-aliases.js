import React from 'react';
import { isEmpty } from 'ramda';
import { useTranslation } from 'react-i18next';

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
  const { t } = useTranslation();

  const { action = {} } = getActionAndCommand(actionData);
  const actionsList = Object.keys(JUKEBOX_ACTIONS_MAP);
  const value = isEmpty(action) ? 0 : action;

  return (
    <FormControl>
      <NativeSelect
        value={value}
        onChange={handleActionChange}
        name="quick-select-actions"
        inputProps={{ 'aria-label': t('cards.controls.select-command-aliases.label') }}
      >
        <option key={0} value={'0'} disabled={true}>
          {t('cards.controls.select-command-aliases.placeholder')}
        </option>
        {actionsList.map((action, key) =>
          <option
            key={key}
            value={actionsList[key]}
          >
            {t(`cards.controls.select-command-aliases.actions.${action}`)}
          </option>
        )}
      </NativeSelect>
    </FormControl>
  );
};

export default SelectCommandAliases;
