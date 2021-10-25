const progressToTime = (duration, progress) => duration * progress / 100;
const timeToProgress = (duration, elapsed) => elapsed * 100 / duration;

const toHHMMSS = (seconds) => {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.round(seconds % 60);
  return [
    h,
    m > 9 ? m : (h ? '0' + m : m || '0'),
    s > 9 ? s : '0' + (isNaN(s) ? '0' : s)
  ].filter(Boolean).join(':');
}

const pluginIsLoaded = (pluginList = {}, _package) => {
  return Object.keys(pluginList).includes(_package)
}

const flatByAlbum = (albumList, { albumartist, album }) => {
  const list = Array.isArray(album)
    ? album.map(name => ({ albumartist, album: name }))
    : [{ albumartist, album }];

  return [...albumList, ...list];
};


export {
  flatByAlbum,
  pluginIsLoaded,
  progressToTime,
  timeToProgress,
  toHHMMSS,
}
