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
  'playerstatus',
  'rfid.card_id',
  'volume.level',
];

// TODO: This is not optimal, we should not know about this path here!
// Let's try to work with relatives paths in the RPC only!
const DEFAULT_AUDIO_DIR = '/home/pi/RPi-Jukebox-RFID/shared/audiofolders';
const ROOT_DIRS = ['./', DEFAULT_AUDIO_DIR];

const JUKEBOX_ACTIONS_MAP = {
  // Command Aliases
  // Player
  play_music: {
    title: 'Play music',
    commands: {
      play_album: {
        title: 'album',
      },
      play_folder: {
        title: 'folder',
      },
      play_single: {
        title: 'song',
      },
    }
  },

  // Volume
  volume: {
    title: 'Volume',
    commands: {
      change_volume: {
        title: 'Change volume by',
      }
    },
  },

  // Host
  host: {
    title: 'System',
    commands: {
      shutdown: {
        title: 'Shutdown',
      },
      reboot: {
        title: 'Reboot',
      },
    }
  }
}

const LABELS = {
  UNKNOW_ARTIST: 'Unknown Artist',
  UNKNOW_ALBUM: 'Unknown Album',
}

export {
  DEFAULT_AUDIO_DIR,
  JUKEBOX_ACTIONS_MAP,
  LABELS,
  PUBSUB_ENDPOINT,
  REQRES_ENDPOINT,
  ROOT_DIRS,
  SUBSCRIPTIONS,
}
