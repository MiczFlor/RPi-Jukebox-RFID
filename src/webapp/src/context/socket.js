import React from 'react';
import * as zmq from 'jszmq';

import { WEBSOCKET_ENDPOINT } from '../config';

const socket_req = zmq.socket('req');
socket_req.connect(WEBSOCKET_ENDPOINT);
const SocketContext = React.createContext();

export {
  socket_req,
  SocketContext,
};
