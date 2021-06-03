import { socket_sub } from './index';
import { decodeMessage } from './utils';

// TODO: Needs refinement once PubSub is implemented on the backend
export const socketEvents = ({ setState }) => {
  socket_sub.on('message', (msg) => {
    const { object, method, params } = decodeMessage(msg);

    if (object && method && params) {
      const playerstatus = params;
      setState(state => { return { ...state, playerstatus } });
    }
    else {
      throw new Error('Received socket message does not match the required format.');
    }
  });
};
