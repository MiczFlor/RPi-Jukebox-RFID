import React from 'react';
import SocketProvider from './context/sockets';

import Player from './components/Player';
import Navigation from './components/Navigation';

function App() {
  return (
    <SocketProvider>
      <Navigation />
      <Player />
    </SocketProvider>
  );
}

export default App;
