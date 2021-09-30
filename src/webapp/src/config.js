const HOST = (window.location.hostname === 'localhost') ?
  '0.0.0.0' :
  window.location.hostname;

const REQRES_ENDPOINT = `ws://${HOST}:5556`;
const PUBSUB_ENDPOINT = `ws://${HOST}:5557`;

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

// const JUKEBOX_ACTIONS_MAP = {
//   // Key is 'package.plugin.method'

//   // Player
//   'player.ctrl.playlistaddplay': {
//     title: 'Play a folder',
//     kwargs: ['folder'],
//   },
//   'player.ctrl.play': {
//     title: 'Play',

//   },
//   'player.ctrl.toggle': {
//     title: 'Toggle',

//   },
//   'player.ctrl.stop': {
//     title: 'Stop',

//   },
//   'player.ctrl.prev': {
//     title: 'Previous song',

//   },
//   'player.ctrl.next': {
//     title: 'Next song',

//   },
//   'player.ctrl.pause': {
//     title: 'Pause',

//   },
//   'player.ctrl.shuffle': {
//     title: 'Set Shuffle',
//     kwargs: ['random'],
//   },
//   'player.ctrl.replay': {
//     title: 'Set Replay',
//   },

//   // Volume
//   'volume.ctrl.set_volume': {
//     title: 'Set volume',
//     kwargs: ['volume'],
//   },
//   'volume.ctrl.dec_volume': {
//     title: 'Decrease volume by',
//     kwargs: ['step'],
//   },
//   'volume.ctrl.inc_volume': {
//     title: 'Increase volume by',
//     kwargs: ['step'],
//   },
//   'volume.ctrl.mute': {
//     title: 'Mute volume',
//     kwargs: ['mute_on'],
//   },
//   'volume.ctrl.unmute': {
//     title: 'Unmute volume',
//   },


// };

export {
  DEFAULT_PLAYER_STATUS,
  JUKEBOX_ACTIONS_MAP,
  PUBSUB_ENDPOINT,
  REQRES_ENDPOINT,
}
