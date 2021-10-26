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
};

export default commands;
