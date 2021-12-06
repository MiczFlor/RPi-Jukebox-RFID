import React, { useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';

import BottomNavigation from '@mui/material/BottomNavigation';
import BottomNavigationAction from '@mui/material/BottomNavigationAction';
import BookmarksIcon from '@mui/icons-material/Bookmarks';
import HomeIcon from '@mui/icons-material/Home';
import MusicNoteIcon from '@mui/icons-material/MusicNote';
import SettingsIcon from '@mui/icons-material/Settings';

export default function Navigation() {
  const { pathname } = useLocation();
  const [value, setValue] = React.useState(0);

  // TODO: This needs to be done smarter!
  useEffect(() => {
    if (pathname.startsWith('/library')) return setValue(1);
    if (pathname.startsWith('/cards')) return setValue(2);
    if (pathname.startsWith('/settings')) return setValue(3);
    return setValue(0);
  }, [pathname]);

  return (
    <BottomNavigation
      value={value}
      onChange={(event, newValue) => {
        setValue(newValue);
      }}
      showLabels
      sx={{
        width: '100%',
        position: 'fixed',
        bottom: '0px',
        paddingBottom: '10px',
      }}
    >
      <BottomNavigationAction
        component={Link}
        to="/"
        label="Start"
        icon={<HomeIcon />}
      />
      <BottomNavigationAction
        component={Link}
        to="/library"
        label="Library"
        icon={<MusicNoteIcon />}
      />
      <BottomNavigationAction
        component={Link}
        to="/cards"
        label="Cards"
        icon={<BookmarksIcon />}
      />
      <BottomNavigationAction
        component={Link}
        to="/settings"
        label="Settings"
        icon={<SettingsIcon />}
      />
    </BottomNavigation>
  );
}
