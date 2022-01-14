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

  const getStepFromSeconds = (seconds) => (
    TIMER_STEPS.indexOf(seconds / 60)
  );

  const [step, setStep] = useState(
    getStepFromSeconds(value)
  );
  const handleChange = (event, step) => setStep(step);

  const handleOnChangeCommitted = (event, value) => (
    onChangeCommitted(event, TIMER_STEPS[value] * 60)
  );

  return (
    <Slider
      value={step}
      marks={marks}
      max={TIMER_STEPS.length-1}
      getAriaValueText={valueLabelFormat}
      valueLabelFormat={valueLabelFormat}
      min={0}
      step={1}
      scale={(value) => TIMER_STEPS[value]}
      valueLabelDisplay="auto"
      onChange={handleChange}
      onChangeCommitted={handleOnChangeCommitted}
    />
  );
};

export default SliderTimer;
