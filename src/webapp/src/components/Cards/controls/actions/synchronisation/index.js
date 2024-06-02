import React from 'react';

import CommandSelector from '../../command-selector';
import OptionsSelector from '../../options-selector';

import { getActionAndCommand } from '../../../utils';

const SelectSynchronisation = ({
  actionData,
  handleActionDataChange,
}) => {
  const { command } = getActionAndCommand(actionData);

  return (
    <>
      <CommandSelector
        actionData={actionData}
        handleActionDataChange={handleActionDataChange}
      />
      {command === 'sync_rfidcards_change_on_rfid_scan' &&
        <OptionsSelector
          actionType="sync_rfidcards_change_on_rfid_scan"
          actionData={actionData}
          handleActionDataChange={handleActionDataChange}
          optionLabel="cards.controls.actions.synchronisation.rfidcards.description"
          options={[
            { labelKey: 'cards.controls.actions.synchronisation.rfidcards.label-toggle', value: 'toggle' },
            { labelKey: 'cards.controls.actions.synchronisation.rfidcards.label-enable', value: 'enable' },
            { labelKey: 'cards.controls.actions.synchronisation.rfidcards.label-disable', value: 'disable' },
          ]}
        />
      }
    </>
  );
};

export default SelectSynchronisation;
