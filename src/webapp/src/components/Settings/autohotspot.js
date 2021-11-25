import React, { useEffect, useState } from 'react';

import {
  Card,
  CardContent,
  CardHeader,
  Divider,
  FormGroup,
  FormControlLabel,
  Grid,
  Switch,
} from '@mui/material';

import request from '../../utils/request';

const SettingsAutoHotpot = () => {
  const [autohotspotStatus, setAutohotspotStatus] = useState('not-installed');

  const toggleAutoHotspot = async () => {
    if (autohotspotStatus === 'active') {
      const { error } = await request('stopAutohotspot');
      return !error && setAutohotspotStatus('inactive');
    }

    const { error } = await request('startAutohotspot');
    return !error && setAutohotspotStatus('active');
  }

  useEffect(() => {
    const fetchAutohotspotStatus = async () => {
      const { result, error } = await request('getAutohotspotStatus');

      if(result) setAutohotspotStatus(result);
      if(error) console.error('RPC Error:', error);
    }

    fetchAutohotspotStatus();
  }, []);

  return (
    <Card>
      <CardHeader title="Auto Hotspot" />
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
                  <Switch
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
