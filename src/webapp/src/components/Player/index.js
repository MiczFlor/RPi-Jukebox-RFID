import React from 'react';

import Display from './display';
import Controls from './controls';

import { PlayerStatusProvider } from '../../context/playerStatus';

const Player = () => {
  return (
    <PlayerStatusProvider>
      <div id="player">
        <Display />
        <Controls />
      </div>
    </PlayerStatusProvider>
  );
};

export default Player;
