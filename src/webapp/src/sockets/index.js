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

const socketEvents = ({ setState }) => {
  socket_sub.on('message', (_topic, _payload) => {
    const { topic, data, error } = decodePubSubMessage(_topic, _payload);

    if (data) {
      setState(state => { return { ...state, [topic]: data } });
      if (topic !== 'playerstatus') {
        console.log(topic, data);
      }
    }

    if (error) {
      // TODO: Better error handling
      console.error(`[PubSub][${topic}]: ${error}`);
    }
  });
};

const initSockets = ({ setState }) => {
  socketEvents({ setState });
};

const socketRequest = (_package, plugin, method, kwargs) => (
  new Promise((resolve, reject) => {
    const requestId = uuidv4();

    socketRequest.server = zmq.socket('req');

    socketRequest.server.on('message', (msg) => {
      const { id, error, result } = decodeMessage(msg);

      if (error && error.message) {
        return reject(error.message);
      }

      socketRequest.server.close();

      if (id && id === requestId) {
        return resolve(result);
      }
      else {
        return reject('Received socket message ID does not match sender ID.');
      }
    });

    socketRequest.server.onerror = function (err) {
      socketRequest.server.close();
      console.error('socket connection error: ', err);
      reject(err);
    };

    socketRequest.server.connect(REQRES_ENDPOINT);

    const payload = preparePayload(
      _package,
      method,
      kwargs,
      requestId,
      plugin,
    );
    socketRequest.server.send(encodeMessage(payload));
  })
);

export {
  initSockets,
  socketRequest,
};
