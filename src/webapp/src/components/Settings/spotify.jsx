import { useCallback, useEffect, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';

import {
  Alert,
  Button,
  Card,
  CardActions,
  CardContent,
  CardHeader,
  CircularProgress,
  Divider,
  IconButton,
  List,
  ListItem,
  ListItemText,
  Tooltip,
  ToggleButton,
  ToggleButtonGroup,
  Typography,
} from '@mui/material';

import LinkIcon from '@mui/icons-material/Link';
import LinkOffIcon from '@mui/icons-material/LinkOff';
import RefreshIcon from '@mui/icons-material/Refresh';

import {
  disconnectSpotify,
  getSpotifyLibrary,
  getSpotifyStatus,
  setSpotifyLibraryMode,
  startSpotifyAuthorization,
} from '../../utils/spotify-api';

const SettingsSpotify = () => {
  const { t } = useTranslation();
  const [status, setStatus] = useState(null);
  const [library, setLibrary] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isUpdatingLibrary, setIsUpdatingLibrary] = useState(false);
  const pollTimer = useRef(null);

  const loadStatus = useCallback(async () => {
    try {
      const [nextStatus, nextLibrary] = await Promise.all([
        getSpotifyStatus(),
        getSpotifyLibrary(),
      ]);
      setStatus(nextStatus);
      setLibrary(nextLibrary);
      setError(null);
      return nextStatus;
    }
    catch (requestError) {
      setError(requestError.message);
      return null;
    }
    finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadStatus();
    return () => window.clearInterval(pollTimer.current);
  }, [loadStatus]);

  const connect = async () => {
    const popup = window.open(
      '',
      'spotify-authorization',
      'popup,width=640,height=760',
    );
    if (!popup) {
      setError(t('settings.spotify.popup-blocked'));
      return;
    }

    setIsLoading(true);
    try {
      const { authorization_url } = await startSpotifyAuthorization();
      popup.location.href = authorization_url;

      window.clearInterval(pollTimer.current);
      pollTimer.current = window.setInterval(async () => {
        const nextStatus = await loadStatus();
        if (nextStatus?.connected || popup.closed) {
          window.clearInterval(pollTimer.current);
          if (!popup.closed) popup.close();
        }
      }, 1500);
    }
    catch (requestError) {
      popup.close();
      setError(requestError.message);
      setIsLoading(false);
    }
  };

  const disconnect = async () => {
    setIsLoading(true);
    try {
      await disconnectSpotify();
      await loadStatus();
    }
    catch (requestError) {
      setError(requestError.message);
      setIsLoading(false);
    }
  };

  const updateLibraryMode = async (_event, mode) => {
    if (!mode) return;
    setIsUpdatingLibrary(true);
    try {
      setLibrary(await setSpotifyLibraryMode(mode));
      setError(null);
    }
    catch (requestError) {
      setError(requestError.message);
    }
    finally {
      setIsUpdatingLibrary(false);
    }
  };

  const stateLabel = !status?.enabled
    ? 'disabled'
    : (!status?.configured
      ? 'not-configured'
      : (status?.connected ? 'connected' : 'not-connected'));

  return (
    <Card>
      <CardHeader
        title={t('settings.spotify.title')}
        action={
          <Tooltip title={t('settings.spotify.refresh')}>
            <span>
              <IconButton
                aria-label={t('settings.spotify.refresh')}
                disabled={isLoading}
                onClick={() => {
                  setIsLoading(true);
                  loadStatus();
                }}
              >
                <RefreshIcon />
              </IconButton>
            </span>
          </Tooltip>
        }
      />
      <Divider />
      <CardContent>
        {isLoading && !status
          ? <CircularProgress size={24} />
          : (
            <List disablePadding>
              <ListItem disableGutters>
                <ListItemText
                  primary={t('settings.spotify.status')}
                  secondary={t(`settings.spotify.states.${stateLabel}`)}
                />
              </ListItem>
              {status?.device_name &&
                <ListItem disableGutters>
                  <ListItemText
                    primary={t('settings.spotify.device')}
                    secondary={status.device_name}
                  />
                </ListItem>
              }
              {status?.redirect_uri &&
                <ListItem disableGutters>
                  <ListItemText
                    primary={t('settings.spotify.redirect-uri')}
                    secondary={status.redirect_uri}
                    slotProps={{
                      secondary: { sx: { overflowWrap: 'anywhere' } },
                    }}
                  />
                </ListItem>
              }
            </List>
          )
        }
        {library &&
          <>
            <Divider sx={{ marginY: 2 }} />
            <Typography component="h3" variant="subtitle1" sx={{ marginBottom: 1 }}>
              {t('settings.spotify.library.title')}
            </Typography>
            <ToggleButtonGroup
              aria-label={t('settings.spotify.library.mode')}
              color="primary"
              disabled={isUpdatingLibrary}
              exclusive
              fullWidth
              onChange={updateLibraryMode}
              size="small"
              value={library.mode}
            >
              <ToggleButton value="account">
                {t('settings.spotify.library.account')}
              </ToggleButton>
              <ToggleButton value="curated">
                {t('settings.spotify.library.curated')}
              </ToggleButton>
            </ToggleButtonGroup>
          </>
        }
        {error && <Alert severity="error">{error}</Alert>}
      </CardContent>
      <CardActions sx={{ justifyContent: 'flex-end' }}>
        {status?.connected
          ? (
            <Button
              disabled={isLoading}
              onClick={disconnect}
              startIcon={<LinkOffIcon />}
            >
              {t('settings.spotify.disconnect')}
            </Button>
          )
          : (
            <Button
              disabled={isLoading || !status?.enabled || !status?.configured}
              onClick={connect}
              startIcon={<LinkIcon />}
              variant="contained"
            >
              {t('settings.spotify.connect')}
            </Button>
          )
        }
      </CardActions>
    </Card>
  );
};

export default SettingsSpotify;
