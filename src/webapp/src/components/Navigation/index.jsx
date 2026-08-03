import { Link, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

import BottomNavigation from '@mui/material/BottomNavigation';
import BottomNavigationAction from '@mui/material/BottomNavigationAction';
import BookmarksIcon from '@mui/icons-material/Bookmarks';
import HomeIcon from '@mui/icons-material/Home';
import MusicNoteIcon from '@mui/icons-material/MusicNote';
import SettingsIcon from '@mui/icons-material/Settings';

export default function Navigation() {
  const { t } = useTranslation();
  const { pathname } = useLocation();
  const value = pathname.startsWith('/library')
    ? 1
    : pathname.startsWith('/cards')
      ? 2
      : pathname.startsWith('/settings')
        ? 3
        : 0;

  return (
    <BottomNavigation
      value={value}
      showLabels
      sx={{
        width: '100%',
        position: 'fixed',
        bottom: '0px',
        height: '65px',
      }}
    >
      <BottomNavigationAction
        component={Link}
        nativeButton={false}
        to="/"
        label={t('navigation.start')}
        icon={<HomeIcon />}
      />
      <BottomNavigationAction
        component={Link}
        nativeButton={false}
        to="/library"
        label={t('navigation.library')}
        icon={<MusicNoteIcon />}
      />
      <BottomNavigationAction
        component={Link}
        nativeButton={false}
        to="/cards"
        label={t('navigation.cards')}
        icon={<BookmarksIcon />}
      />
      <BottomNavigationAction
        component={Link}
        nativeButton={false}
        to="/settings"
        label={t('navigation.settings')}
        icon={<SettingsIcon />}
      />
    </BottomNavigation>
  );
}
