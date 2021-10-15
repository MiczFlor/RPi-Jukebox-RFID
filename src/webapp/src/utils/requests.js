import { socketRequest } from "../sockets";

const getMusicCoverByFilenameAsBase64 = async (audio_src) => {
  try {
    const result = await socketRequest('music_cover_art', 'ctrl', 'get_by_filename_as_base64', { audio_src });
    return { result };
  }
  catch (error) {
    console.error('registerCard error: ', error);
    return { error };
  };
}

const fetchDirectoryTreeOfAudiofolder = async () => {
  try {
    const result = await socketRequest('player', 'ctrl', 'list_all_dirs');
    return { result };
  }
  catch(error) {
    console.error('registerCard error: ', error);
    return { error };
  }
};

const fetchCardsList = async () => {
  try {
    const result = await socketRequest('cards', 'list_cards');

    return { result };
  }
  catch (error) {
    console.error('registerCard error: ', error);

    return { error };
  };
};

const registerCard = async (kwargs) => {
  try {
    const result = await socketRequest('cards', 'register_card', null, kwargs);
    return { result };
  }
  catch (error) {
    console.error('registerCard error: ', error);
    return { error };
  }
};

const deleteCard = async (card_id) => {
  try {
    const result = await socketRequest('cards', 'delete_card', null, { card_id: card_id.toString() });
    return { result };
  }
  catch (error) {
    return { error };
  }
};

export {
  getMusicCoverByFilenameAsBase64,
  fetchDirectoryTreeOfAudiofolder,
  fetchCardsList,
  deleteCard,
  registerCard,
}
