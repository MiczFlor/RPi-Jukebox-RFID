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

    // Each call gets its own local socket instance (previously a shared `socketRequest.server`
    // static field was reassigned on every call and never closed - see git history). With many
    // requests in flight at once (e.g. lazy-loaded cover art, or repeatedly navigating into the
    // library), that leaked an ever-growing number of open Req sockets, all still registered as
    // peers of the server's REP socket, which degraded and eventually stalled the WebUI over
    // time. Using a local variable makes it safe to close the socket once this specific request
    // is done, without risking closing a different in-flight request's socket.
    const socket = new zmq.Req();

    const cleanup = () => {
      try {
        socket.close();
      } catch (closeError) {
        // Already closed / never fully connected - nothing to do.
      }
    };

    socket.on('message', (msg) => {
      const { id, error, result } = decodeMessage(msg);
      cleanup();

      if (error && error.message) {
        return reject(error.message);
      }

      if (id && id === requestId) {
        return resolve(result);
      }
      else {
        return reject('Received socket message ID does not match sender ID.');
      }
    });

    socket.onerror = function (err) {
      cleanup();
      reject(err);
    };

    try {
      socket.connect(REQRES_ENDPOINT);
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
    socket.send(encodeMessage(payload));
  })
);

export {
  initSockets,
  socketRequest,
};
