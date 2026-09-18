import { expect, test } from 'vitest';

import commands from '../../commands';
import {
  buildActionData,
  getArgsValues,
} from './utils';


test('timer commands map and default the restart argument', () => {
  for (const command of [
    'timer_fade_volume',
    'timer_idle_shutdown',
    'timer_shutdown',
    'timer_stop_player',
  ]) {
    expect(commands[command].argKeys).toEqual(['wait_seconds', 'restart']);
  }

  const legacy = buildActionData(
    'timers',
    'timer_shutdown',
    [300],
  );
  expect(getArgsValues(legacy)).toEqual([300, true]);

  const explicit = buildActionData(
    'timers',
    'timer_shutdown',
    [300, false],
  );
  expect(getArgsValues(explicit)).toEqual([300, false]);
});

test('player card contracts preserve provider-qualified content', () => {
  expect(commands.play_single.argKeys).toEqual(['song_url', 'provider']);
  expect(commands.play_album.argKeys).toEqual([
    'albumartist',
    'album',
    'content_uri',
    'provider',
  ]);

  const providerAlbum = buildActionData('play_music', 'play_album', {
    albumartist: 'Artist',
    album: 'Album',
    content_uri: 'service:album:123',
    provider: 'streaming',
  });
  expect(getArgsValues(providerAlbum)).toEqual([
    'Artist',
    'Album',
    'service:album:123',
    'streaming',
  ]);

  const legacyAlbum = buildActionData(
    'play_music',
    'play_album',
    ['Artist', 'Album'],
  );
  expect(getArgsValues(legacyAlbum)).toEqual([
    'Artist',
    'Album',
    undefined,
    undefined,
  ]);
});

test('jellyfin card contracts preserve stable URIs and the provider', () => {
  const albumAction = buildActionData('play_music', 'play_album', {
    albumartist: 'Artist One',
    album: 'Album One',
    content_uri: 'service:jellyfin:album:album-1',
    provider: 'jellyfin',
  });
  expect(getArgsValues(albumAction)).toEqual([
    'Artist One',
    'Album One',
    'service:jellyfin:album:album-1',
    'jellyfin',
  ]);

  const trackAction = buildActionData('play_music', 'play_single', {
    song_url: 'service:jellyfin:track:track-1',
    provider: 'jellyfin',
  });
  expect(getArgsValues(trackAction)).toEqual([
    'service:jellyfin:track:track-1',
    'jellyfin',
  ]);
});
