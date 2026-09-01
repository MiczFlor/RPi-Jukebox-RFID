import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import {
  Alert,
  Box,
  Button,
  Card,
  CardActions,
  CardContent,
  CardHeader,
  CircularProgress,
  Divider,
  FormControlLabel,
  Grid,
  InputAdornment,
  Switch,
  TextField,
  Tooltip,
} from '@mui/material';

import LockIcon from '@mui/icons-material/Lock';
import SaveIcon from '@mui/icons-material/Save';
import WifiTetheringIcon from '@mui/icons-material/WifiTethering';

import request from '../../utils/request';

const SettingsJellyfin = () => {
  const { t } = useTranslation();
  const [settings, setSettings] = useState(null);
  const [form, setForm] = useState({});
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isTesting, setIsTesting] = useState(false);
  const [testError, setTestError] = useState(null);
  const [testResult, setTestResult] = useState(null);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const loadSettings = async () => {
    setIsLoading(true);
    setError(null);
    const { result, error: requestError } = await request('getJellyfinSettings');
    if (requestError) {
      setError(typeof requestError === 'string'
        ? requestError
        : requestError.message);
      setIsLoading(false);
      return;
    }
    const loaded = result || {};
    setSettings(loaded);
    setForm({
      enabled: Boolean(loaded.enabled),
      host: loaded.host || '',
      username: loaded.username || '',
      // Secrets are never pre-filled: the backend only reports whether
      // they are configured (has_api_key / has_password).
      api_key: '',
      password: '',
      catalog_cache_ttl: loaded.catalog_cache_ttl ?? 300,
      request_timeout: loaded.request_timeout ?? 30,
    });
    setIsLoading(false);
  };

  useEffect(() => {
    loadSettings();
  }, []);

  const handleChange = (key) => (event) => {
    setForm((previous) => ({
      ...previous,
      [key]: event.target.type === 'checkbox'
        ? event.target.checked
        : event.target.value,
    }));
    setSuccess(false);
    if (key === 'host') setTestResult(null);
  };

  const handleTestConnection = async () => {
    setIsTesting(true);
    setTestError(null);
    setTestResult(null);
    const { result, error: requestError } = await request(
      'testJellyfinConnection',
      { host: String(form.host || '').trim() },
    );
    if (requestError) {
      setTestError(typeof requestError === 'string'
        ? requestError
        : requestError.message);
      setIsTesting(false);
      return;
    }
    setTestResult(result || { found: false, url: null, candidates: [] });
    setIsTesting(false);
  };

  const handleAdoptFoundAddress = () => {
    if (testResult?.url) {
      setForm((previous) => ({ ...previous, host: testResult.url }));
      setSuccess(false);
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    setError(null);
    setSuccess(false);

    const payload = {
      enabled: Boolean(form.enabled),
      host: String(form.host || '').trim(),
      username: String(form.username || '').trim(),
      catalog_cache_ttl: Number(form.catalog_cache_ttl),
      request_timeout: Number(form.request_timeout),
    };
    // Secrets are only transmitted when the user typed a new value. An
    // empty field keeps the stored secret, which is never sent back.
    if (form.api_key) payload.api_key = form.api_key;
    if (form.password) payload.password = form.password;

    const { error: requestError } = await request('setJellyfinSettings', {
      settings: payload,
    });
    if (requestError) {
      setError(typeof requestError === 'string'
        ? requestError
        : requestError.message);
      setIsSaving(false);
      return;
    }
    await loadSettings();
    setIsSaving(false);
    setSuccess(true);
  };

  const renderSecretField = (key, label, configured) => (
    <TextField
      fullWidth
      label={label}
      onChange={handleChange(key)}
      placeholder={configured ? t('settings.jellyfin.secret-keep') : ''}
      size="small"
      slotProps={configured ? {
        input: {
          endAdornment: (
            <InputAdornment position="end">
              <Tooltip title={t('settings.jellyfin.secret-configured')}>
                <LockIcon
                  data-testid="jellyfin-secret-lock"
                  fontSize="small"
                />
              </Tooltip>
            </InputAdornment>
          ),
        },
      } : undefined}
      type="password"
      value={form[key] || ''}
    />
  );

  if (isLoading && !settings) {
    return (
      <Card>
        <CardHeader title={t('settings.jellyfin.title')} />
        <Divider />
        <CardContent>
          <CircularProgress size={24} />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader title={t('settings.jellyfin.title')} />
      <Divider />
      <CardContent>
        <Grid container spacing={2} sx={{ flexDirection: 'column' }}>
          <Grid>
            <FormControlLabel
              control={
                <Switch
                  checked={Boolean(form.enabled)}
                  onChange={handleChange('enabled')}
                />
              }
              label={t('settings.jellyfin.enabled')}
            />
          </Grid>
          <Grid>
            <Grid container spacing={1} sx={{ flexWrap: 'nowrap' }}>
              <Grid sx={{ flexGrow: 1 }}>
                <TextField
                  fullWidth
                  label={t('settings.jellyfin.host')}
                  onChange={handleChange('host')}
                  placeholder="192.168.1.10"
                  size="small"
                  value={form.host || ''}
                />
              </Grid>
              <Grid sx={{ alignSelf: 'center' }}>
                <Button
                  disabled={isTesting || !String(form.host || '').trim()}
                  onClick={handleTestConnection}
                  startIcon={isTesting
                    ? <CircularProgress size={16} />
                    : <WifiTetheringIcon />}
                  variant="outlined"
                >
                  {t('settings.jellyfin.test')}
                </Button>
              </Grid>
            </Grid>
            {testError &&
              <Alert severity="error" sx={{ marginTop: 1 }}>
                {testError}
              </Alert>
            }
            {testResult?.found &&
              <Alert severity="success" sx={{ marginTop: 1 }}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Box sx={{ flexGrow: 1 }}>
                    {t('settings.jellyfin.test-found', { url: testResult.url })}
                  </Box>
                  <Button
                    onClick={handleAdoptFoundAddress}
                    size="small"
                  >
                    {t('settings.jellyfin.test-adopt')}
                  </Button>
                </Box>
              </Alert>
            }
            {testResult && !testResult.found &&
              <Alert severity="warning" sx={{ marginTop: 1 }}>
                {t('settings.jellyfin.test-not-found')}
                {testResult.candidates?.length > 0 && (
                  <Box sx={{ marginTop: 0.5 }}>
                    {t('settings.jellyfin.test-candidates')}
                    <Box component="ul" sx={{ margin: 0.5, paddingLeft: 2 }}>
                      {testResult.candidates.map((candidate) => (
                        <li key={candidate}>{candidate}</li>
                      ))}
                    </Box>
                  </Box>
                )}
              </Alert>
            }
          </Grid>
          <Grid>
            {renderSecretField(
              'api_key',
              t('settings.jellyfin.api-key'),
              Boolean(settings?.has_api_key),
            )}
          </Grid>
          <Grid>
            <TextField
              fullWidth
              label={t('settings.jellyfin.username')}
              onChange={handleChange('username')}
              size="small"
              value={form.username || ''}
            />
          </Grid>
          <Grid>
            {renderSecretField(
              'password',
              t('settings.jellyfin.password'),
              Boolean(settings?.has_password),
            )}
          </Grid>
          <Grid>
            <TextField
              fullWidth
              label={t('settings.jellyfin.catalog-cache-ttl')}
              onChange={handleChange('catalog_cache_ttl')}
              size="small"
              type="number"
              value={form.catalog_cache_ttl ?? ''}
            />
          </Grid>
          <Grid>
            <TextField
              fullWidth
              label={t('settings.jellyfin.request-timeout')}
              onChange={handleChange('request_timeout')}
              size="small"
              type="number"
              value={form.request_timeout ?? ''}
            />
          </Grid>
          <Grid>
            <Alert severity="info">
              {t('settings.jellyfin.secret-warning')}
            </Alert>
          </Grid>
          <Grid>
            <Alert severity="info">
              {t('settings.jellyfin.restart-hint')}
            </Alert>
          </Grid>
          {error &&
            <Grid>
              <Alert severity="error">{error}</Alert>
            </Grid>
          }
          {success &&
            <Grid>
              <Alert severity="success">{t('settings.jellyfin.saved')}</Alert>
            </Grid>
          }
        </Grid>
      </CardContent>
      <CardActions sx={{ justifyContent: 'flex-end' }}>
        <Button
          disabled={isSaving}
          onClick={handleSave}
          startIcon={<SaveIcon />}
          variant="contained"
        >
          {t('settings.jellyfin.save')}
        </Button>
      </CardActions>
    </Card>
  );
};

export default SettingsJellyfin;
