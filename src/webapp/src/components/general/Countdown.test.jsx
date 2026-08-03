import { act, render, screen } from '@testing-library/react';
import {
  afterEach,
  beforeEach,
  expect,
  test,
  vi,
} from 'vitest';

import Countdown from './Countdown';


beforeEach(() => {
  vi.useFakeTimers();
  vi.setSystemTime(0);
});

afterEach(() => {
  vi.useRealTimers();
});

test('resets its local deadline when authoritative state changes', () => {
  const { rerender } = render(
    <Countdown resetKey={1} seconds={5} stringEnded="Done" />,
  );
  expect(screen.getByText('0:05')).toBeVisible();

  act(() => {
    vi.advanceTimersByTime(2000);
  });
  expect(screen.getByText('0:03')).toBeVisible();

  rerender(
    <Countdown resetKey={2} seconds={10} stringEnded="Done" />,
  );
  expect(screen.getByText('0:10')).toBeVisible();
});

test('clamps at zero and only changes its display on expiry', () => {
  render(<Countdown resetKey={1} seconds={1} stringEnded="Done" />);

  act(() => {
    vi.advanceTimersByTime(1500);
  });

  expect(screen.getByText('Done')).toBeVisible();
});
