import { socket_sub } from './index';
import { decodePubSubMessage } from './utils';

export const socketEvents = ({ setState }) => {
  socket_sub.on('message', (msg) => {
    const message = decodePubSubMessage(msg);

    switch(message?.topic) {
      case 'playerstatus':
        const { playerstatus } = message;

        if (playerstatus) {
          setState(state => { return { ...state, playerstatus } });
          break;
        }
        console.error('[PubSub][playerstatus] Payload missing');
        break;

      case 'ping':
        console.log('ping');
    }
  });
};
