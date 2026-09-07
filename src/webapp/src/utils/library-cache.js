const albumListCache = new Map();

const clearAlbumListCache = () => {
  albumListCache.clear();
};

export {
  albumListCache,
  clearAlbumListCache,
};
