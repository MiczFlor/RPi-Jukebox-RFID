import { socket_req } from './index';
import { encodeMessage } from './utils';

const sendRequest = (obj) => {
  socket_req.send(encodeMessage(obj));
}

const execCommand = (object, method, params = {}) => {
  const payload = {
    object,
    method,
    params,
  };

  sendRequest(payload);
}

const getPlayerStatus = () => {
  execCommand('player', 'playerstatus');
};

export {
  execCommand,
  getPlayerStatus,
}