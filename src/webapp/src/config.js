const WEBSOCKET_ENDPOINT = 'ws://0.0.0.0:5556';

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

export {
  DEFAULT_PLAYER_STATUS,
  WEBSOCKET_ENDPOINT,
}
