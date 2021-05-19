import React from 'react';
import { SocketContext, socket_req } from './context/socket';

import Container from '@material-ui/core/Container';
import Player from './components/Player/index';

function App() {
  return (
    <SocketContext.Provider value={socket_req}>
      <Container maxWidth="sm">
        <Player />
      </Container>
    </SocketContext.Provider>
  );
}

export default App;
