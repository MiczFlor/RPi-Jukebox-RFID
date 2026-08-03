import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { expect, test, vi } from 'vitest';

import request from '../../../utils/request';
import ActionsControls from './actions-controls';


vi.mock('../../../utils/request', () => ({
  default: vi.fn().mockResolvedValue({ result: null }),
}));
vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: key => ({
      'general.buttons.delete': 'Delete',
      'general.buttons.save': 'Save',
    })[key] || key,
  }),
}));

test('saving a legacy timer card submits restart=true', async () => {
  const user = userEvent.setup();
  render(
    <MemoryRouter initialEntries={['/cards/123/edit']}>
      <Routes>
        <Route
          path="/cards/:cardId/edit"
          element={
            <ActionsControls
              actionData={{
                action: 'timers',
                command: {
                  name: 'timer_shutdown',
                  args: { wait_seconds: 300 },
                },
              }}
              cardId="123"
            />
          }
        />
        <Route path="/cards" element={<div>Cards</div>} />
      </Routes>
    </MemoryRouter>,
  );

  await user.click(screen.getByRole('button', { name: 'Save' }));

  await waitFor(() => {
    expect(request).toHaveBeenCalledWith('registerCard', {
      card_id: '123',
      cmd_alias: 'timer_shutdown',
      overwrite: true,
      args: [300, true],
    });
  });
});
