import {
  afterEach,
  beforeEach,
  describe,
  expect,
  test,
  vi,
} from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import request from '../../utils/request';
import SettingsJellyfin from './jellyfin';

vi.mock('../../utils/request', () => ({
  default: vi.fn(),
}));

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key) => key,
  }),
}));

const baseSettings = {
  enabled: false,
  host: '',
  username: '',
  has_password: false,
  catalog_cache_ttl: 300,
  request_timeout: 30,
};

const renderJellyfin = () => render(<SettingsJellyfin />);

describe('SettingsJellyfin', () => {
  beforeEach(() => {
    request.mockReset();
    request.mockResolvedValue({ result: baseSettings, error: null });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  test('loads the settings and renders the secret field empty and masked', async () => {
    renderJellyfin();

    expect(await screen.findByLabelText('settings.jellyfin.host'))
      .toBeInTheDocument();
    expect(request).toHaveBeenCalledWith('getJellyfinSettings');

    const password = screen.getByLabelText('settings.jellyfin.password');
    // The secret is never pre-filled and must be a masked input.
    expect(password).toHaveAttribute('type', 'password');
    expect(password).toHaveValue('');
  });

  test('marks a stored password without revealing it', async () => {
    request.mockResolvedValue({
      result: { ...baseSettings, has_password: true },
      error: null,
    });
    renderJellyfin();

    await screen.findByLabelText('settings.jellyfin.host');
    expect(screen.getByTestId('jellyfin-secret-lock'))
      .toBeInTheDocument();
    expect(screen.getByLabelText('settings.jellyfin.password'))
      .toHaveValue('');
  });

  test('saves without transmitting empty secret fields', async () => {
    const user = userEvent.setup();
    renderJellyfin();
    await screen.findByLabelText('settings.jellyfin.host');

    await user.click(
      screen.getByRole('button', { name: 'settings.jellyfin.save' }),
    );

    expect(request).toHaveBeenCalledWith('setJellyfinSettings', {
      settings: {
        enabled: false,
        host: '',
        username: '',
        catalog_cache_ttl: 300,
        request_timeout: 30,
      },
    });
    expect(await screen.findByText('settings.jellyfin.saved'))
      .toBeInTheDocument();
  });

  test('transmits a newly typed password and clears the field afterwards', async () => {
    const user = userEvent.setup();
    renderJellyfin();
    await screen.findByLabelText('settings.jellyfin.host');

    await user.type(
      screen.getByLabelText('settings.jellyfin.password'),
      'new-pw',
    );
    await user.click(
      screen.getByRole('button', { name: 'settings.jellyfin.save' }),
    );

    expect(request).toHaveBeenCalledWith('setJellyfinSettings', {
      settings: expect.objectContaining({
        password: 'new-pw',
      }),
    });
    expect(await screen.findByText('settings.jellyfin.saved'))
      .toBeInTheDocument();
    expect(screen.getByLabelText('settings.jellyfin.password')).toHaveValue('');
  });

  test('shows backend errors from the save request', async () => {
    request.mockResolvedValueOnce({ result: baseSettings, error: null });
    request.mockResolvedValueOnce({
      result: null,
      error: 'Jellyfin is enabled but no server host is set',
    });
    const user = userEvent.setup();
    renderJellyfin();
    await screen.findByLabelText('settings.jellyfin.host');

    await user.click(
      screen.getByRole('button', { name: 'settings.jellyfin.save' }),
    );

    expect(
      await screen.findByText(
        'Jellyfin is enabled but no server host is set',
      ),
    ).toBeInTheDocument();
  });

  test('tests the connection and adopts the found address', async () => {
    const user = userEvent.setup();
    request.mockImplementation(async (command) => {
      if (command === 'getJellyfinSettings') {
        return { result: baseSettings, error: null };
      }
      if (command === 'testJellyfinConnection') {
        return {
          result: {
            found: true,
            url: 'https://192.168.1.10:8920',
            candidates: [
              'http://192.168.1.10:8096',
              'https://192.168.1.10:8920',
            ],
          },
          error: null,
        };
      }
      return { result: null, error: null };
    });
    renderJellyfin();

    await user.type(
      await screen.findByLabelText('settings.jellyfin.host'),
      '192.168.1.10',
    );
    await user.click(
      screen.getByRole('button', { name: 'settings.jellyfin.test' }),
    );

    expect(request).toHaveBeenCalledWith('testJellyfinConnection', {
      host: '192.168.1.10',
    });
    expect(
      await screen.findByText('settings.jellyfin.test-found'),
    ).toBeInTheDocument();

    await user.click(
      screen.getByRole('button', { name: 'settings.jellyfin.test-adopt' }),
    );
    expect(screen.getByLabelText('settings.jellyfin.host'))
      .toHaveValue('https://192.168.1.10:8920');
  });

  test('shows the tested candidates when no server is found', async () => {
    const user = userEvent.setup();
    request.mockImplementation(async (command) => {
      if (command === 'getJellyfinSettings') {
        return { result: baseSettings, error: null };
      }
      if (command === 'testJellyfinConnection') {
        return {
          result: {
            found: false,
            url: null,
            candidates: [
              'http://192.168.1.10:8096',
              'https://192.168.1.10:8920',
            ],
          },
          error: null,
        };
      }
      return { result: null, error: null };
    });
    renderJellyfin();

    await user.type(
      await screen.findByLabelText('settings.jellyfin.host'),
      '192.168.1.10',
    );
    await user.click(
      screen.getByRole('button', { name: 'settings.jellyfin.test' }),
    );

    expect(
      await screen.findByText('settings.jellyfin.test-not-found'),
    ).toBeInTheDocument();
    expect(screen.getByText('http://192.168.1.10:8096')).toBeInTheDocument();
    expect(screen.getByText('https://192.168.1.10:8920')).toBeInTheDocument();
  });

  test('shows errors from the connection test', async () => {
    request.mockResolvedValueOnce({ result: baseSettings, error: null });
    request.mockResolvedValueOnce({
      result: null,
      error: 'Connection test failed',
    });
    const user = userEvent.setup();
    renderJellyfin();

    await user.type(
      await screen.findByLabelText('settings.jellyfin.host'),
      '192.168.1.10',
    );
    await user.click(
      screen.getByRole('button', { name: 'settings.jellyfin.test' }),
    );

    expect(
      await screen.findByText('Connection test failed'),
    ).toBeInTheDocument();
  });
});
