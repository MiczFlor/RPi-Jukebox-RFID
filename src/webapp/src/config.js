const HOST = (window.location.hostname === 'localhost') ?
  '0.0.0.0' :
  window.location.hostname;

const REQRES_ENDPOINT = `ws://${HOST}:5556`;
const PUBSUB_ENDPOINT = `ws://${HOST}:5557`;

const SUBSCRIPTIONS = [
  'batt_status',
  'core.plugins.loaded',
  'core.version',
  'core.started_at',
  'host.timer.cputemp',
  'host.temperature.cpu',
  'playerstatus',
  'rfid.card_id',
  'volume.level',
];

const ROOT_DIR = './';

// TODO: The reason why thos commands are empty objects is due to a legacy
// situation where titles associated with those commands were stored here
// After the intro of i18n, those titles became obsolete. Because changing
// the data structure from object to array requires some refactoring, this
// was not done yet to maintain functionality. It's ok to change the command
// object keys to arrays, but some downstream methods need to change as well
const JUKEBOX_ACTIONS_MAP = {
  // Command Aliases
  // Player
  play_music: {
    commands: {
      play_album: {},
      play_folder: {},
      play_single: {},
    }
  },

  // Audio & Volume
  audio: {
    commands: {
      change_volume: {},
      toggle_output: {},
      play: {},
      pause: {},
      toggle: {},
      next_song: {},
      prev_song: {},
      shuffle: {},
      repeat: {},
    },
  },

  // Host
  host: {
    commands: {
      shutdown: {},
      reboot: {},
      say_my_ip: {},
    }
  },

  // Timers
  timers: {
    commands: {
      timer_shutdown: {},
      timer_stop_player: {},
      timer_fade_volume: {},
    }
  },

  // Synchronisation
  synchronisation: {
    commands: {
      sync_rfidcards_all: {},
      sync_rfidcards_change_on_rfid_scan: {},
    }
  },
}

const TIMER_STEPS = [0, 2, 5, 10, 15, 20, 30, 45, 60, 120, 180, 240];

export {
  JUKEBOX_ACTIONS_MAP,
  PUBSUB_ENDPOINT,
  REQRES_ENDPOINT,
  ROOT_DIR,
  SUBSCRIPTIONS,
  TIMER_STEPS,
}
