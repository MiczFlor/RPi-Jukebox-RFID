import * as zmq from 'jszmq';

import { PUBSUB_ENDPOINT, REQRES_ENDPOINT } from '../config';
import { socketEvents } from './events';
import { decodeMessage, encodeMessage } from './utils';

const SUBSCRIPTIONS = ['ping', 'playerstatus'];

const socket_sub = new zmq.Sub();

SUBSCRIPTIONS.forEach(
  (topic) => socket_sub.subscribe(topic)
);

socket_sub.connect(PUBSUB_ENDPOINT);

const initSockets = ({ setState }) => {
  socketEvents({ setState });
};

const socketRequest = (payload) => (
  new Promise((resolve, reject) => {
    socketRequest.server = zmq.socket('req');

    socketRequest.server.on('message', (msg) => {
      // TODO: Should be corrected!
      const { object, method, params = {} } = decodeMessage(msg);

      socketRequest.server.close();

      if (object && method && params) {
        resolve(params);
      }
      else {
        reject('Received socket message does not match the required format.');
      }
    });

    socketRequest.server.onerror = function (err) {
      socketRequest.server.close();
      console.error("socket connection error : ", err);
      reject(err);
    };

    socketRequest.server.connect(REQRES_ENDPOINT);
    socketRequest.server.send(encodeMessage(payload));
  })
);

export {
  socket_sub,
  socketRequest,
  initSockets,
};


