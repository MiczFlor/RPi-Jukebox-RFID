const HOST = (window.location.hostname === 'localhost') ?
  '0.0.0.0' :
  window.location.hostname;

const REQRES_ENDPOINT = `ws://${HOST}:5556`;
const PUBSUB_ENDPOINT = `ws://${HOST}:5557`;

const SUBSCRIPTIONS = [
  'core.plugins.loaded',
  'core.started_at',
  'playerstatus',
  'rfid.card_id',
  'volume.level',
];

const JUKEBOX_ACTIONS_MAP = {
  // Command Aliases
  // Player
  // 'play_card': {
  //   title: 'Play a folder',
  //   argKeys: ['folder']
  // },

  'play_album': {
    title: 'Play a album',
    argKeys: ['album', 'albumartist']
  },

  // Volume
  'change_volume': {
    title: 'Change volume by',
    argKeys: ['step']
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
