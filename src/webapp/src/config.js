const HOST = (window.location.hostname === 'localhost') ?
  '0.0.0.0' :
  window.location.hostname;

const REQRES_ENDPOINT = `ws://${HOST}:5556`;
const PUBSUB_ENDPOINT = `ws://${HOST}:5557`;

const SUBSCRIPTIONS = [
  'core.plugins.loaded',
  'playerstatus',
  'rfid.card_id',
];

const JUKEBOX_ACTIONS_MAP = {
  // Command Aliases

  // Player
  'play_card': {
    title: 'Play a album',
    args: ['folder']
  },

  // Volume
  'inc_volume': {
    title: 'Increase volume by',
    args: ['step']
  },

  'dec_volume': {
    title: 'Decrease volume by',
    args: ['step']
  },

  // Host
  'shutdown': {
    title: 'Shutdown',
  },
  'reboot': {
    title: 'Reboot',
  },
}

const LABELS = {
  UNKNOW_ARTIST: 'Unknown Artist',
  UNKNOW_ALBUM: 'Unknown Album',
}

export {
  JUKEBOX_ACTIONS_MAP,
  LABELS,
  PUBSUB_ENDPOINT,
  REQRES_ENDPOINT,
  SUBSCRIPTIONS,
}
