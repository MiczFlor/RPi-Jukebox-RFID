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

// The backend RPC server is single-threaded and processes one request at a time no matter what,
// so there is no real concurrency to gain by opening a separate connection per call - only cost.
// Earlier versions opened a brand-new zmq.Req() (i.e. a brand-new WebSocket + ZMTP handshake)
// for *every single* RPC call. Even after closing each socket once its response arrived (see git
// history), a burst of near-simultaneous calls (a single UI interaction easily fires half a dozen:
// play + get_volume + get_soft_max_volume + get_single_coverart, ...) could still momentarily
// flood the connection with many new handshakes at once, observed as the WebUI going completely
// unresponsive for several seconds before catching up. A single persistent Req socket, with calls
// serialized through a small FIFO queue, avoids the connection churn entirely and matches what the
// server can actually do concurrently anyway.
//
// A REQ socket enforces strict request/reply lock-step - it can only have one outstanding
// request at a time. Since everything now funnels through this single socket, a request that
// never gets a reply would otherwise wedge every subsequent call forever. The backend bounds its
// own worst case (MPD timeout etc.) to ~10s, so 15s here is a safety net, not the expected case.
const REQUEST_TIMEOUT_MS = 15000;

let persistentSocket = null;
let isProcessingQueue = false;
let currentRequest = null;
const requestQueue = [];

const discardSocket = () => {
  if (persistentSocket !== null) {
    try {
      persistentSocket.close();
    } catch (closeError) {
      // Already closed / never fully connected - nothing to do.
    }
    persistentSocket = null;
  }
};

const getPersistentSocket = () => {
  if (persistentSocket === null) {
    persistentSocket = new zmq.Req();
    persistentSocket.onerror = (err) => {
      console.error(`ZMQ socket error on '${REQRES_ENDPOINT}': `, err);
      // The socket is unusable now - reject whatever was waiting on it and start fresh so the
      // queue doesn't stay wedged forever, instead of leaving every future call hanging too.
      discardSocket();
      isProcessingQueue = false;
      if (currentRequest !== null) {
        const { reject } = currentRequest;
        currentRequest = null;
        reject(err);
      }
      processRequestQueue();
    };
    try {
      persistentSocket.connect(REQRES_ENDPOINT);
    }
    catch (error) {
      console.error(`WebSocket connection to '${REQRES_ENDPOINT} failed: `, error);
    }
  }
  return persistentSocket;
};

const processRequestQueue = () => {
  if (isProcessingQueue || requestQueue.length === 0) return;

  const request = requestQueue.shift();
  const { requestId, payload, resolve, reject } = request;
  isProcessingQueue = true;
  currentRequest = request;
  const socket = getPersistentSocket();

  const finish = (fn, value) => {
    if (currentRequest !== request) return; // already handled (e.g. by the timeout/error path)
    clearTimeout(timeoutHandle);
    currentRequest = null;
    isProcessingQueue = false;
    fn(value);
    processRequestQueue();
  };

  const timeoutHandle = setTimeout(() => {
    console.error(`RPC request timed out after ${REQUEST_TIMEOUT_MS}ms - resetting connection`);
    discardSocket();
    finish(reject, 'Request timed out');
  }, REQUEST_TIMEOUT_MS);

  socket.once('message', (msg) => {
    const { id, error, result } = decodeMessage(msg);

    if (error && error.message) {
      finish(reject, error.message);
    }
    else if (id && id === requestId) {
      finish(resolve, result);
    }
    else {
      finish(reject, 'Received socket message ID does not match sender ID.');
    }
  });

  socket.send(encodeMessage(payload));
};

const socketRequest = (_package, plugin, method, kwargs) => (
  new Promise((resolve, reject) => {
    const requestId = uuidv4();
    const payload = preparePayload(
      requestId,
      _package,
      plugin,
      method,
      kwargs,
    );

    requestQueue.push({ requestId, payload, resolve, reject });
    processRequestQueue();
  })
);

export {
  initSockets,
  socketRequest,
};
