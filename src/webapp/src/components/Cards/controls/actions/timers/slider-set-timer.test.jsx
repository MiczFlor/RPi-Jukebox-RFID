import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { expect, test, vi } from 'vitest';

import SliderSetTimer from './slider-set-timer';


vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: key => ({
      'cards.controls.actions.timers.description': 'Timer duration',
      'cards.controls.actions.timers.restart': 'Restart existing timer',
    })[key] || key,
  }),
}));

test('legacy timer cards default restart on and persist checkbox changes', async () => {
  const user = userEvent.setup();
  const handleActionDataChange = vi.fn();
  render(
    <SliderSetTimer
      actionData={{
        action: 'timers',
        command: {
          name: 'timer_shutdown',
          args: { wait_seconds: 300 },
        },
      }}
      handleActionDataChange={handleActionDataChange}
    />,
  );

  const restart = screen.getByRole('checkbox', {
    name: 'Restart existing timer',
  });
  expect(restart).toBeChecked();
  await user.click(restart);

  expect(handleActionDataChange).toHaveBeenCalledWith(
    'timers',
    'timer_shutdown',
    {
      wait_seconds: 300,
      restart: false,
    },
  );
});
