import { act, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {
  afterEach,
  beforeEach,
  expect,
  test,
  vi,
} from 'vitest';

import PubSubContext from '../../../context/pubsub/context';
import request from '../../../utils/request';
import Timer, { useTimer } from './timer';


vi.mock('../../../utils/request', () => ({
  default: vi.fn(),
}));
vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: key => ({
      'settings.timers.shutdown.title': 'Shut Down',
      'settings.timers.shutdown.label': 'Shutdown timer',
      'settings.timers.ended': 'Done',
      'settings.timers.set': 'Set timer',
      'settings.timers.cancel': 'Cancel',
    })[key] || key,
  }),
}));

const provider = (state, child) => (
  <PubSubContext.Provider value={{ state, setState: vi.fn() }}>
    {child}
  </PubSubContext.Provider>
);

const deferred = () => {
  let resolve;
  const promise = new Promise(promiseResolve => {
    resolve = promiseResolve;
  });
  return { promise, resolve };
};

beforeEach(() => {
  request.mockResolvedValue({
    result: {
      enabled: false,
      remaining_seconds: 0,
    },
  });
});

afterEach(() => {
  vi.clearAllMocks();
  vi.useRealTimers();
});

test('uses RPC initially and publisher events for remote restart and cancel', async () => {
  request.mockResolvedValueOnce({
    result: {
      enabled: true,
      remaining_seconds: 60,
    },
  });
  const { rerender } = render(provider({}, <Timer type="shutdown" />));

  expect(await screen.findByText('1:00')).toBeVisible();

  rerender(provider({
    'timers.timer_shutdown': {
      enabled: true,
      remaining_seconds: 120,
    },
  }, <Timer type="shutdown" />));
  expect(await screen.findByText('2:00')).toBeVisible();

  rerender(provider({
    'timers.timer_shutdown': {
      enabled: false,
      remaining_seconds: 0,
    },
  }, <Timer type="shutdown" />));
  expect(await screen.findByRole('button', { name: 'Set timer' })).toBeVisible();
});

test('does not let a late RPC fallback overwrite publisher state', async () => {
  const rpc = deferred();
  request.mockReturnValueOnce(rpc.promise);
  const { rerender } = render(provider({}, <Timer type="shutdown" />));

  rerender(provider({
    'timers.timer_shutdown': {
      enabled: true,
      remaining_seconds: 300,
    },
  }, <Timer type="shutdown" />));
  expect(await screen.findByText('5:00')).toBeVisible();

  await act(async () => {
    rpc.resolve({
      result: {
        enabled: false,
        remaining_seconds: 0,
      },
    });
    await rpc.promise;
  });

  expect(screen.getByText('5:00')).toBeVisible();
});

test('local countdown expiry does not cancel the backend timer', async () => {
  vi.useFakeTimers();
  vi.setSystemTime(0);
  render(provider({
    'timers.timer_shutdown': {
      enabled: true,
      remaining_seconds: 1,
    },
  }, <Timer type="shutdown" />));

  await act(async () => {
    await Promise.resolve();
    vi.advanceTimersByTime(1500);
  });

  expect(screen.getByText('Done')).toBeVisible();
  expect(request).not.toHaveBeenCalledWith('timer_shutdown.cancel');
});

const HookHarness = () => {
  const timer = useTimer('shutdown');
  return (
    <>
      <button onClick={() => timer.setTimer(300)}>Start</button>
      <button onClick={timer.cancelTimer}>Cancel timer</button>
    </>
  );
};

test('start relies on backend restart defaults without cancelling first', async () => {
  const user = userEvent.setup();
  render(provider({}, <HookHarness />));
  await waitFor(() => (
    expect(request).toHaveBeenCalledWith('timer_shutdown.get_state')
  ));
  request.mockClear();

  await user.click(screen.getByRole('button', { name: 'Start' }));

  expect(request).toHaveBeenCalledWith(
    'timer_shutdown',
    { wait_seconds: 300 },
  );
  expect(request).not.toHaveBeenCalledWith('timer_shutdown.cancel');
});
