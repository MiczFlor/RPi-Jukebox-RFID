import { socket_req } from './index';
import { decodeMessage } from './utils';

export const socketEvents = ({ setValue }) => {
  socket_req.on('message', (msg) => {
    const { object, method, params } = decodeMessage(msg);

    if (object && method && params) {
      const playerStatus = params;
      setValue(state => { return { ...state, playerStatus } });
    }
    else {
      throw new Error('Received socket message does not match the required format.');
    }
  });

  socket_req.on('terminated', (msg) => {
    throw new Error('Socket connection was terminated.', msg);
  });
};
