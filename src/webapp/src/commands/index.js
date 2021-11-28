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
  playSong: {
    _package: 'player',
    plugin: 'ctrl',
    method: 'play_single',
  },
  playFolder: {
    _package: 'player',
    plugin: 'ctrl',
    method: 'play_folder',
  },
  playAlbum: {
    _package: 'player',
    plugin: 'ctrl',
    method: 'play_album',
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
  getMaxVolume: {
    _package: 'volume',
    plugin: 'ctrl',
    method: 'get_max_volume',
  },
  setMaxVolume: {
    _package: 'volume',
    plugin: 'ctrl',
    method: 'set_max_volume',
  },
  toggleMuteVolume: {
    _package: 'volume',
    plugin: 'ctrl',
    method: 'mute',
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
  reboot: {
    _package: 'host',
    plugin: 'reboot',
  },
  shutdown: {
    _package: 'host',
    plugin: 'shutdown',
  },
};

export default commands;
