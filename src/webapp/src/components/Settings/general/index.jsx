import { useTranslation } from 'react-i18next';

import { useTheme } from '@mui/material/styles';

import {
  Card,
  CardContent,
  CardHeader,
  Divider,
  Grid,
} from '@mui/material';
import ShowCovers from './show-covers';

const SettingsGeneral = () => {
  const { t } = useTranslation();
  const theme = useTheme();
  const spacer = { marginBottom: theme.spacing(2) }

  return (
    <Card>
      <CardHeader
        title={t('settings.general.title')}
      />
      <Divider />
      <CardContent>
        <Grid
          container
          sx={{
            '& > .MuiGrid-root:not(:last-child)': spacer,
            flexDirection: 'column',
          }}
        >
          <ShowCovers />
        </Grid>
      </CardContent>
    </Card>
  );
};

export default SettingsGeneral;
