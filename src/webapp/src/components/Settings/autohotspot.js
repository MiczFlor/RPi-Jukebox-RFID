import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import {
  Card,
  CardContent,
  CardHeader,
  Divider,
  FormGroup,
  FormControlLabel,
  Grid,
  Link,
} from '@mui/material';

import { SwitchWithLoader } from '../general';

import request from '../../utils/request';

const helpUrl = 'https://github.com/MiczFlor/RPi-Jukebox-RFID/blob/future3/main/documentation/builders/autohotspot.md';

const SettingsAutoHotpot = () => {
  const { t } = useTranslation();
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
        title={t('settings.autohotspot.title')}
        subheader={
          autohotspotStatus === 'not-installed' &&
          <>
            {`⚠️ ${t('settings.autohotspot.not-installed')}`}
            <Link
              href={helpUrl}
              target="_blank"
              rel="noreferrer"
              sx={{
                marginLeft: '10px'
              }}
            >
              {t('settings.autohotspot.why')}
            </Link>
          </>
        }
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
                label={t('settings.autohotspot.control-label')}
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
