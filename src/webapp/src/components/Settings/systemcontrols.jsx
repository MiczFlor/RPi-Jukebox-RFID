import { useTranslation } from 'react-i18next';

import {
  Card,
  CardContent,
  CardHeader,
  Divider,
  Grid,
} from '@mui/material';

import RebootDialog from './dialogs/reboot';
import ShutDownDialog from './dialogs/shutdown';

const SystemControls = () => {
  const { t } = useTranslation();

  return (
    <Card>
      <CardHeader title={t('settings.systemcontrols.title')} />
      <Divider />
      <CardContent>
        <Grid
          container
          sx={{
            alignItems: 'center',
            justifyContent: 'space-around',
          }}
        >
          <Grid>
            <RebootDialog />
          </Grid>
          <Grid>
            <ShutDownDialog />
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};

export default SystemControls;
