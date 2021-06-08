const REQRES_ENDPOINT = 'ws://0.0.0.0:5556';
const PUBSUB_ENDPOINT = 'ws://0.0.0.0:5557';

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
  PUBSUB_ENDPOINT,
  REQRES_ENDPOINT,
}
