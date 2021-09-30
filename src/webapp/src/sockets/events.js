import { socket_sub } from './index';
import { decodePubSubMessage } from './utils';

export const socketEvents = ({ setState }) => {
  socket_sub.on('message', (_topic, _payload) => {
    const message = decodePubSubMessage(_topic, _payload);

    switch(message?.topic) {
      case 'playerstatus':
        const { playerstatus } = message;

        if (playerstatus) {
          setState(state => { return { ...state, playerstatus } });
          break;
        }
        console.error('[PubSub][playerstatus] Payload missing');
        break;

      case 'rfid.card_id':
        console.log('[PubSub][rfid.card_id]: ', _payload);
        break;

      default:
        break;
    }
  });
};
