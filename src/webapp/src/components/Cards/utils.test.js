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
