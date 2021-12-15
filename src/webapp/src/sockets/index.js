import { v4 as uuidv4 } from 'uuid';
import * as zmq from 'jszmq';

import {
  PUBSUB_ENDPOINT,
  REQRES_ENDPOINT,
  SUBSCRIPTIONS,
} from '../config';
import {
  decodeMessage,
  decodePubSubMessage,
  encodeMessage,
  preparePayload
} from './utils';

const socket_sub = new zmq.Sub();

SUBSCRIPTIONS.forEach(
  (topic) => socket_sub.subscribe(topic)
);

socket_sub.connect(PUBSUB_ENDPOINT);

const socketEvents = ({ setState, events = [] }) => {
  socket_sub.on('message', (_topic, _payload) => {
    const { topic, data, error } = decodePubSubMessage(_topic, _payload);

    if (events.includes(topic) && data) {
      setState(state => ({ ...state, [topic]: data }));
      if (topic !== 'playerstatus') {
        console.log(topic, data, events);
      }
    }

    if (error) {
      // TODO: Better error handling
      console.error(`[PubSub][${topic}]: ${error}`);
    }
  });
};

const initSockets = ({ setState, events }) => {
  socketEvents({ setState, events });
};

const socketRequest = (_package, plugin, method, kwargs) => (
  new Promise((resolve, reject) => {
    const requestId = uuidv4();

    socketRequest.server = new zmq.Req();

    socketRequest.server.on('message', (msg) => {
      const { id, error, result } = decodeMessage(msg);

      if (error && error.message) {
        return reject(error.message);
      }

      // This implementation of Req Sockets is not ideal for parallel
      // requests. In case 2 requests are launched at the same time
      // both connect to the socket. The first one to return would
      // close the channel which cancels the second request without
      // allowing to receive the data. Not closing the channel
      // here is not ideal, but it's not harmful either.
      // Ideally, we outsouce `socketRequest.server` similar to
      // `socket_sub`
      // socketRequest.server.close();

      if (id && id === requestId) {
        return resolve(result);
      }
      else {
        return reject('Received socket message ID does not match sender ID.');
      }
    });

    socketRequest.server.onerror = function (err) {
      reject(err);
    };

    try {
      socketRequest.server.connect(REQRES_ENDPOINT);
    }
    catch (error) {
      console.error(`WebSocket connection to '${REQRES_ENDPOINT} failed: `, error);
    }

    const payload = preparePayload(
      requestId,
      _package,
      plugin,
      method,
      kwargs,
    );
    socketRequest.server.send(encodeMessage(payload));
  })
);

export {
  initSockets,
  socketRequest,
};
