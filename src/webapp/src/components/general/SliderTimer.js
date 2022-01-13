import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';

import { Slider } from '@mui/material';

import { TIMER_STEPS } from '../../config';

const SliderTimer = ({ onChangeCommitted, value }) => {
  const { t } = useTranslation();

  const marks = TIMER_STEPS.map((value, index) => (
    { label: value, value: index }
  ));

  const valueLabelFormat = (value) => {
    if (value === 0) return t('settings.timers.option-label-off');
    return t('settings.timers.option-label-timeslot', { value });
  }

  const [step, setStep] = useState(value);
  const handleChange = (event, step) => setStep(step);

  return (
    <Slider
      value={step || value}
      marks={marks}
      max={TIMER_STEPS.length-1}
      getAriaValueText={valueLabelFormat}
      valueLabelFormat={valueLabelFormat}
      min={0}
      step={1}
      scale={(value) => TIMER_STEPS[value]}
      valueLabelDisplay="auto"
      onChange={handleChange}
      onChangeCommitted={onChangeCommitted}
    />
  );
};

export default SliderTimer;
