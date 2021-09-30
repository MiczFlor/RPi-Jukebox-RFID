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

const DEFAULT_PLAYER_STATUS = {
  kwargs: {
    status: {
      consume: "0",
      mixrampdb: "0.000000",
      playlist: "1",
      playlistlength: "0",
      random: "0",
      repeat: "0",
      single: "0",
      state: "stop",
      volume: 60,
    }
  }
};

const JUKEBOX_ACTIONS_MAP = {
  // Quick Selects / QS

  // Player
  'play_card': {
    title: 'Play a folder',
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

export {
  DEFAULT_PLAYER_STATUS,
  JUKEBOX_ACTIONS_MAP,
  PUBSUB_ENDPOINT,
  REQRES_ENDPOINT,
  SUBSCRIPTIONS,
}
