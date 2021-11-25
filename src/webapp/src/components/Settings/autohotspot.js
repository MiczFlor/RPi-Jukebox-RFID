import React, { useEffect, useState } from 'react';

import {
  Card,
  CardContent,
  CardHeader,
  Divider,
  FormGroup,
  FormControlLabel,
  Grid,
} from '@mui/material';

import { SwitchWithLoader } from '../custom';

import request from '../../utils/request';

const SettingsAutoHotpot = () => {
  const [autohotspotStatus, setAutohotspotStatus] = useState('not-installed');
  const [isLoading, setIsLoading] = useState(true);

  const getAutohotspotStatus = async () => {
    const { result, error } = await request('getAutohotspotStatus');

    if(result && result !== 'error') setAutohotspotStatus(result);
    if((result && result === 'error') || error) console.error(error);
  }

  const toggleAutoHotspot = async () => {
    const status = autohotspotStatus === 'active' ? 'inactive' : 'active';
    const action = autohotspotStatus === 'active' ? 'stop' : 'start';

    setIsLoading(true);
    setAutohotspotStatus(status);
    const { result, error } = await request(`${action}Autohotspot`);

    if (error || result === 'error') {
      console.error(`An error occured while performing '${action}AutoHotspot'`);
      await getAutohotspotStatus();
    }

    setIsLoading(false);
  }

  useEffect(() => {
    const fetchAutohotspotStatus = async () => {
      setIsLoading(true);
      await getAutohotspotStatus();
      setIsLoading(false);
    }

    fetchAutohotspotStatus();
  }, []);

  return (
    <Card>
      <CardHeader
        title="Auto Hotspot"
        subheader={autohotspotStatus === 'not-installed' && '⚠️ This feature is not installed'}
      />
      <Divider />
      <CardContent>
        <Grid container direction="column">
          <Grid item>
            <FormGroup>
              <FormControlLabel
                sx={{
                  justifyContent: 'space-between',
                  marginLeft: '0',
                }}
                control={
                  <SwitchWithLoader
                    isLoading={isLoading}
                    checked={autohotspotStatus === 'active'}
                    disabled={autohotspotStatus === 'not-installed'}
                    onChange={() => toggleAutoHotspot()}
                  />
                }
                label="Enable Auto Hotspot"
                labelPlacement="start"
              />
            </FormGroup>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};

export default SettingsAutoHotpot;
