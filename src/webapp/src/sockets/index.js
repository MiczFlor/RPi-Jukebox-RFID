import * as zmq from 'jszmq';

import { WEBSOCKET_ENDPOINT } from '../config';
import { socketEvents } from './events';
import { getPlayerStatus } from './emit';

const socket_req = zmq.socket('req');
socket_req.connect(WEBSOCKET_ENDPOINT);

const initSockets = ({ setValue }) => {
  socketEvents({ setValue });
  getPlayerStatus();
};

export {
  socket_req,
  initSockets,
};
