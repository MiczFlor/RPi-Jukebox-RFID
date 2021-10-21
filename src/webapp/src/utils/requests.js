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

const getFlattenListOfDirectories = async () => {
  const list = await socketRequest('player', 'ctrl', 'list_all_dirs');
  return list.filter(entry => !!entry.directory);
};

const fetchCardsList = async (setIsLoading) => {
  setIsLoading(true);

  try {
    const result = await socketRequest('cards', 'list_cards');
    setIsLoading(false);
    return { result };
  }
  catch (error) {
    console.error('registerCard error: ', error);
    setIsLoading(false);
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

const getMaxVolume = async () => {
  try {
    const result = await socketRequest('volume', 'ctrl', 'get_max_volume');
    return { result };
  }
  catch (error) {
    console.error('getMaxVolume error: ', error);
    return { error };
  }
};

const setMaxVolume = async (max_volume) => {
  try {
    const result = await socketRequest('volume', 'ctrl', 'set_max_volume', { max_volume });
    return { result };
  }
  catch (error) {
    console.error('setMaxVolume error: ', error);
    return { error };
  }
};

export {
  getMusicCoverByFilenameAsBase64,
  getFlattenListOfDirectories,
  fetchCardsList,
  deleteCard,
  registerCard,
  getMaxVolume,
  setMaxVolume,
}
