import React from 'react';

import CommandSelector from '../../command-selector';
import SliderChangeVolume from './slider-change-volume';
import ShuffleOptions from './shuffle-options';

import { getActionAndCommand } from '../../../utils';

const SelectAudioVolume = ({
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
      {command === 'change_volume' &&
        <SliderChangeVolume
          actionData={actionData}
          handleActionDataChange={handleActionDataChange}
        />
      }
      {command === 'set_shuffle' &&
        <ShuffleOptions
          actionData={actionData}
          handleActionDataChange={handleActionDataChange}
        />
      }
    </>
  );
};

export default SelectAudioVolume;