import { socketRequest } from "../sockets";

const getMusicCoverByFilenameAsBase64 = async (audio_src) => {
  try {
    const result = await socketRequest('music_cover_art', 'ctrl', 'get_by_filename_as_base64', { audio_src });
    return { result };
  }
  catch (error) {
    console.error('get_by_filename_as_base64 error: ', error);
    return { error };
  };
}

const fetchDirectoryTreeOfAudiofolder = async () => {
  try {
    const result = await socketRequest('player', 'ctrl', 'list_all_dirs');
    return { result };
  }
  catch(error) {
    console.error('list_all_dirs error: ', error);
    return { error };
  }
};

const fetchAlbumList = async () => {
  try {
    const result = await socketRequest('player', 'ctrl', 'list_albums');

    return { result };
  }
  catch (error) {
    console.error('list_albums error: ', error);
    return { error };
  };
};

const fetchSongList = async (artist, album) => {
  try {
    const result = await socketRequest(
      'player', 'ctrl', 'list_song_by_artist_and_album',
      { artist, album }
    );

    return { result };
  }
  catch (error) {
    console.error('list_albums error: ', error);
    return { error };
  };
};

const fetchCardsList = async () => {
  try {
    const result = await socketRequest('cards', 'list_cards');

    return { result };
  }
  catch (error) {
    console.error('list_cards error: ', error);
    return { error };
  };
};

const registerCard = async (kwargs) => {
  try {
    const result = await socketRequest('cards', 'register_card', null, kwargs);
    return { result };
  }
  catch (error) {
    console.error('register_card error: ', error);
    return { error };
  }
};

const deleteCard = async (card_id) => {
  try {
    const result = await socketRequest('cards', 'delete_card', null, { card_id: card_id.toString() });
    return { result };
  }
  catch (error) {
    console.error('delete_card error: ', error);
    return { error };
  }
};

export {
  getMusicCoverByFilenameAsBase64,
  fetchAlbumList,
  fetchCardsList,
  fetchDirectoryTreeOfAudiofolder,
  fetchSongList,
  deleteCard,
  registerCard,
}
