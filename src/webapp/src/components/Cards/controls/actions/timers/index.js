import React from 'react';

import CommandSelector from '../../command-selector';
import SliderSetTimer from './slider-set-timer';

import { getActionAndCommand } from '../../../utils';

const SelectTimers = ({
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
      {command &&
        <SliderSetTimer
          actionData={actionData}
          handleActionDataChange={handleActionDataChange}
        />
      }
    </>
  );
};

export default SelectTimers;