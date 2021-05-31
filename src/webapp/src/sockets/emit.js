import { socket_req } from './index';
import { encodeMessage } from './utils';

const sendRequest = (obj) => {
  socket_req.send(encodeMessage(obj));
}

const execCommand = (plugin, method, kwargs = {}) => {
  const payload = {
    plugin,
    method,
    kwargs,
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