import React from 'react';

import SettingsAutoShutdown from './autoshutdown';
import SettingsSecondSwipe from './secondswipe';
import SystemControls from './systemcontrols';
import SettingsVolume from './volume';

const Settings = () => {
  return (
    <div id="settings">
      <SystemControls />
      <SettingsVolume />
      <SettingsAutoShutdown />
      <SettingsSecondSwipe />
    </div>
  );
};

export default Settings;
