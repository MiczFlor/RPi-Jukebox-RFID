import React from 'react';

import SettingsAutoShutdown from './autoshutdown';
import SettingsInterface from './interfaces';
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
      <SettingsInterface />
    </div>
  );
};

export default Settings;
