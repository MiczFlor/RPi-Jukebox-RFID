import React from 'react';

import CommandSelector from '../../command-selector';
import SliderChangeVolume from './slider-change-volume';
import OptionsSelector from '../../options-selector';

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
      {command === 'shuffle' &&
        <OptionsSelector
          actionType="audio_shuffle"
          actionData={actionData}
          handleActionDataChange={handleActionDataChange}
          optionLabel="cards.controls.actions.audio.shuffle.description"
          options={[
            { labelKey: 'cards.controls.actions.audio.shuffle.label-toggle', value: 'toggle' },
            { labelKey: 'cards.controls.actions.audio.shuffle.label-enable', value: 'enable' },
            { labelKey: 'cards.controls.actions.audio.shuffle.label-disable', value: 'disable' },
          ]}
        />
      }
      {command === 'repeat' &&
        <OptionsSelector
          actionType="audio_repeat"
          actionData={actionData}
          handleActionDataChange={handleActionDataChange}
          optionLabel="cards.controls.actions.audio.repeat.description"
          options={[
            { labelKey: 'cards.controls.actions.audio.repeat.label-toggle', value: 'toggle' },
            { labelKey: 'cards.controls.actions.audio.repeat.label-toggle-repeat', value: 'toggle_repeat' },
            { labelKey: 'cards.controls.actions.audio.repeat.label-toggle-repeat-single', value: 'toggle_repeat_single' },
            { labelKey: 'cards.controls.actions.audio.repeat.label-enable-repeat', value: 'enable_repeat' },
            { labelKey: 'cards.controls.actions.audio.repeat.label-enable-repeat-single', value: 'enable_repeat_single' },
            { labelKey: 'cards.controls.actions.audio.repeat.label-disable', value: 'disable' },
          ]}
        />
      }
    </>
  );
};

export default SelectAudioVolume;