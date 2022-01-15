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

// TODO: This is not optimal, we should not know about this path here!
// Let's try to work with relatives paths in the RPC only!
const DEFAULT_AUDIO_DIR = '/home/pi/RPi-Jukebox-RFID/shared/audiofolders';
const ROOT_DIRS = ['./', DEFAULT_AUDIO_DIR];


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
      toggle_output: {}
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
}

const TIMER_STEPS = [0, 2, 5, 10, 15, 20, 30, 45, 60, 120, 180, 240];

export {
  DEFAULT_AUDIO_DIR,
  JUKEBOX_ACTIONS_MAP,
  PUBSUB_ENDPOINT,
  REQRES_ENDPOINT,
  ROOT_DIRS,
  SUBSCRIPTIONS,
  TIMER_STEPS,
}
