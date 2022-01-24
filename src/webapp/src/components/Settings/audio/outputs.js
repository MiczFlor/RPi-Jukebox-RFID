import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { findIndex, propEq } from 'ramda';

import {
  CircularProgress,
  Grid,
  FormControl,
  FormControlLabel,
  Radio,
  RadioGroup,
  Typography,
} from '@mui/material';

import request from '../../../utils/request';

const Outputs = () => {
  const { t } = useTranslation();

  const [activeSink, setActiveSink] = useState(null);
  const [sinkList, setSinkList] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isError, setIsError] = useState(false);

  const setOutput = (event, sink_index) => {
    setActiveSink(sink_index);

    setIsLoading(true);
    (async () => {
      await request('setAudioOutput', { sink_index: parseInt(sink_index) });
    })();
    setIsLoading(false);
  }

  useEffect(() => {
    const fetchAudioOutputs = async () =>  {
      const {
        result: { active_sink, sink_list },
        error
      } = await request('getAudioOutputs');
      setIsLoading(false);

      if (error) {
        setIsError(true);
        return console.error(error);
      }

      const activeSinkIndex = findIndex(
        propEq('pulse_sink_name', active_sink)
      )(sink_list);

      setActiveSink(activeSinkIndex);
      setSinkList(sink_list);
    }

    fetchAudioOutputs();
  }, []);

  return (
    <Grid container direction="column">
      <Grid container direction="row" justifyContent="space-between" alignItems="center">
        <Typography>{t('settings.audio.outputs.title')}</Typography>
        {isLoading && <CircularProgress size={20} />}
        {isError && <Typography>⚠️</Typography>}
      </Grid>
      <FormControl component="fieldset">
          <RadioGroup
            aria-label={t('settings.audio.outputs.title')}
            name="audio-outputs"
            value={activeSink}
            onChange={setOutput}
          >
            {sinkList.map(({ alias }, index) =>
              <FormControlLabel
                control={<Radio />}
                label={alias}
                key={index}
                value={index}
              />
            )}
          </RadioGroup>
        </FormControl>
    </Grid>
  );
};

export default Outputs;
