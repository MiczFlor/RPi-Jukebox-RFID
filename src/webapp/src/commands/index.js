const commands = {
  musicCoverByFilenameAsBase64: {
    _package: 'music_cover_art',
    plugin: 'ctrl',
    method: 'get_by_filename_as_base64',
  },
  directoryTreeOfAudiofolder: {
    _package: 'player',
    plugin: 'ctrl',
    method: 'list_all_dirs',
  },
  albumList: {
    _package: 'player',
    plugin: 'ctrl',
    method: 'list_albums',
  },
  songList: {
    _package: 'player',
    plugin: 'ctrl',
    method: 'list_song_by_artist_and_album',
  },
  getSongByUrl: {
    _package: 'player',
    plugin: 'ctrl',
    method: 'get_song_by_url',
    argKeys: ['song_url']
  },
  folderList: {
    _package: 'player',
    plugin: 'ctrl',
    method: 'get_folder_content',
  },
  cardsList: {
    _package: 'cards',
    plugin: 'list_cards',
  },
  registerCard: {
    _package: 'cards',
    plugin: 'register_card',
  },
  deleteCard: {
    _package: 'cards',
    plugin: 'delete_card',
  },
  playerstatus: {
    _package: 'player',
    plugin: 'ctrl',
    method: 'playerstatus'
  },

  // Player Actions
  play: {
    _package: 'player',
    plugin: 'ctrl',
    method: 'play',
  },
  play_single: {
    _package: 'player',
    plugin: 'ctrl',
    method: 'play_single',
    argKeys: ['song_url']
  },
  play_folder: {
    _package: 'player',
    plugin: 'ctrl',
    method: 'play_folder',
    argKeys: ['folder']
  },
  play_album: {
    _package: 'player',
    plugin: 'ctrl',
    method: 'play_album',
    argKeys: ['albumartist', 'album']
  },
  pause: {
    _package: 'player',
    plugin: 'ctrl',
    method: 'pause',
  },
  previous: {
    _package: 'player',
    plugin: 'ctrl',
    method: 'prev',
  },
  next: {
    _package: 'player',
    plugin: 'ctrl',
    method: 'next',
  },
  shuffle: {
    _package: 'player',
    plugin: 'ctrl',
    method: 'shuffle',
  },
  repeat: {
    _package: 'player',
    plugin: 'ctrl',
    method: 'repeatmode',
  },
  seek: {
    _package: 'player',
    plugin: 'ctrl',
    method: 'seek',
  },

  // Volume
  setVolume: {
    _package: 'volume',
    plugin: 'ctrl',
    method: 'set_volume',
  },
  getVolume: {
    _package: 'volume',
    plugin: 'ctrl',
    method: 'get_volume',
  },
  getMaxVolume: {
    _package: 'volume',
    plugin: 'ctrl',
    method: 'get_soft_max_volume',
  },
  setMaxVolume: {
    _package: 'volume',
    plugin: 'ctrl',
    method: 'set_soft_max_volume',
  },
  change_volume: {
    _package: 'volume',
    plugin: 'ctrl',
    method: 'change_volume',
    argKeys: ['step'],
  },
  toggleMuteVolume: {
    _package: 'volume',
    plugin: 'ctrl',
    method: 'mute',
  },
  getAudioOutputs: {
    _package: 'volume',
    plugin: 'ctrl',
    method: 'get_outputs',
  },
  setAudioOutput: {
    _package: 'volume',
    plugin: 'ctrl',
    method: 'set_output',
    argKeys: ['sink_index'],
  },
  toggle_output: {
    _package: 'volume',
    plugin: 'ctrl',
    method: 'toggle_output',
  },

  // Timers
  'timer_fade_volume.cancel': {
    _package: 'timers',
    plugin: 'timer_fade_volume',
    method: 'cancel',
  },
  'timer_fade_volume.get_state': {
    _package: 'timers',
    plugin: 'timer_fade_volume',
    method: 'get_state',
  },
  'timer_fade_volume': {
    _package: 'timers',
    plugin: 'timer_fade_volume',
    method: 'start',
    argKeys: ['wait_seconds'],
  },
  'timer_shutdown.cancel': {
    _package: 'timers',
    plugin: 'timer_shutdown',
    method: 'cancel',
  },
  'timer_shutdown.get_state': {
    _package: 'timers',
    plugin: 'timer_shutdown',
    method: 'get_state',
  },
  'timer_shutdown': {
    _package: 'timers',
    plugin: 'timer_shutdown',
    method: 'start',
    argKeys: ['wait_seconds'],
  },
  'timer_stop_player.cancel': {
    _package: 'timers',
    plugin: 'timer_stop_player',
    method: 'cancel',
  },
  'timer_stop_player.get_state': {
    _package: 'timers',
    plugin: 'timer_stop_player',
    method: 'get_state',
  },
  'timer_stop_player': {
    _package: 'timers',
    plugin: 'timer_stop_player',
    method: 'start',
    argKeys: ['wait_seconds'],
  },


  // Host
  getAutohotspotStatus: {
    _package: 'host',
    plugin: 'get_autohotspot_status',
  },
  startAutohotspot: {
    _package: 'host',
    plugin: 'start_autohotspot',
  },
  stopAutohotspot: {
    _package: 'host',
    plugin: 'stop_autohotspot',
  },
  getIpAddress: {
    _package: 'host',
    plugin: 'get_ip_address',
  },
  getDiskUsage: {
    _package: 'host',
    plugin: 'get_disk_usage',
  },
  reboot: {
    _package: 'host',
    plugin: 'reboot',
  },
  shutdown: {
    _package: 'host',
    plugin: 'shutdown',
  },
  say_my_ip: {
    _package: 'host',
    plugin: 'say_my_ip',
    argKeys: ['option'],
  },
};

export default commands;
