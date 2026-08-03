import { expect, test } from '@playwright/test';

const rpcResults = {
  get_app_settings: { show_covers: false },
  get_autohotspot_status: 'inactive',
  get_disk_usage: { used: 8_000, total: 32_000 },
  get_folder_content: [
    {
      name: 'Albums',
      relpath: 'Music/Rock/Albums',
      type: 'directory',
    },
    {
      name: 'sample.mp3',
      relpath: 'Music/Rock/sample.mp3',
      type: 'file',
    },
  ],
  get_ip_address: '192.168.1.42',
  get_outputs: {
    active_sink: 'speaker',
    sink_list: [
      { alias: 'Built-in speaker', pulse_sink_name: 'speaker' },
      { alias: 'USB audio', pulse_sink_name: 'usb' },
    ],
  },
  get_soft_max_volume: 80,
  get_state: {
    enabled: false,
    remaining_seconds: 0,
    running: false,
  },
  get_volume: 42,
  get_single_coverart: 'test-cover.png',
  list_albums: [
    { albumartist: 'Daft Punk', album: ['Discovery', 'Random Access Memories'] },
    { albumartist: 'Massive Attack', album: 'Mezzanine' },
  ],
  list_cards: {
    '0001234567': {
      action: { args: [] },
      from_alias: '',
      func: 'play',
    },
  },
};

const socketEvents = {
  'batt_status': { charging: false, soc: 76 },
  'core.plugins.loaded': { battmon: true },
  'core.version': '3.7.0-alpha',
  'host.temperature.cpu': '47.2',
  'host.timer.cputemp': { enabled: true },
  'playerstatus': {
    album: 'Discovery',
    artist: 'Daft Punk',
    duration: '224',
    elapsed: '42',
    file: 'Daft Punk/Discovery/One More Time.mp3',
    random: '0',
    repeat: '0',
    single: '0',
    songid: '1',
    state: 'play',
    title: 'One More Time',
  },
  'volume.level': { mute: false, volume: 42 },
};

async function mockBackend(
  page,
  { failRpc = false, rpcGate, showCovers = false } = {},
) {
  const libraryCalls = [];
  const rpcCalls = [];

  await page.addInitScript(() => {
    window.localStorage.setItem('i18nextLng', 'en');
  });

  await page.route('**/api/v1/library/entries**', async route => {
    const requestUrl = new URL(route.request().url());
    libraryCalls.push(requestUrl.searchParams.get('folder'));
    await route.fulfill({
      body: JSON.stringify({
        entries: rpcResults.get_folder_content,
      }),
      contentType: 'application/json',
      status: 200,
    });
  });

  await page.route('**/api/v1/rpc', async route => {
    const request = route.request();
    const payload = request.postDataJSON();
    rpcCalls.push(payload);

    if (rpcGate) {
      await rpcGate;
    }

    if (failRpc) {
      await route.fulfill({
        body: JSON.stringify({ error: 'Backend unavailable' }),
        contentType: 'application/json',
        status: 503,
      });
      return;
    }

    const key = payload.method || payload.plugin;
    const result = key === 'get_app_settings'
      ? { show_covers: showCovers }
      : rpcResults[key] ?? null;
    await route.fulfill({
      body: JSON.stringify({
        id: payload.id,
        result,
      }),
      contentType: 'application/json',
      status: 200,
    });
  });

  await page.route('**/cover-cache/test-cover.png', route => route.fulfill({
    contentType: 'image/png',
    path: 'public/logo192.png',
    status: 200,
  }));

  await page.routeWebSocket('**/api/v1/events', socket => {
    socket.onMessage(message => {
      const payload = JSON.parse(message);
      if (payload.type !== 'subscribe') {
        return;
      }

      payload.topics.forEach(topic => {
        if (topic in socketEvents) {
          socket.send(JSON.stringify({
            type: 'event',
            topic,
            data: socketEvents[topic],
          }));
        }
      });
    });
  });

  return { libraryCalls, rpcCalls };
}

async function expectStableLayout(page) {
  await expect(page.locator('#root')).not.toBeEmpty();
  await expect(page.locator('.MuiBottomNavigation-root')).toBeVisible();

  const layout = await page.evaluate(() => {
    const actions = Array.from(
      document.querySelectorAll('.MuiBottomNavigationAction-root'),
      element => element.getBoundingClientRect(),
    );
    const nav = document.querySelector('.MuiBottomNavigation-root')
      .getBoundingClientRect();
    const actionRows = Array.from(document.querySelectorAll('.MuiListItem-root'));

    return {
      horizontalOverflow: document.documentElement.scrollWidth > window.innerWidth,
      navWithinViewport: nav.top >= 0 && nav.bottom <= window.innerHeight + 1,
      overlappingContentActions: actionRows.some(row => {
        const text = row.querySelector('.MuiListItemText-root');
        const action = row.querySelector(
          '.MuiButton-root, .MuiIconButton-root, .MuiSwitch-root',
        );
        if (!text || !action) {
          return false;
        }

        const textRect = text.getBoundingClientRect();
        const actionRect = action.getBoundingClientRect();
        return (
          textRect.left < actionRect.right &&
          textRect.right > actionRect.left &&
          textRect.top < actionRect.bottom &&
          textRect.bottom > actionRect.top
        );
      }),
      overlappingActions: actions.some((action, index) => (
        actions.slice(index + 1).some(other => (
          action.left < other.right &&
          action.right > other.left &&
          action.top < other.bottom &&
          action.bottom > other.top
        ))
      )),
    };
  });

  expect(layout).toEqual({
    horizontalOverflow: false,
    navWithinViewport: true,
    overlappingContentActions: false,
    overlappingActions: false,
  });
}

async function expectAbove(top, bottom) {
  const [topBox, bottomBox] = await Promise.all([
    top.boundingBox(),
    bottom.boundingBox(),
  ]);

  expect(topBox.y + topBox.height).toBeLessThanOrEqual(bottomBox.y);
}

function collectConsoleErrors(page) {
  const errors = [];
  page.on('console', message => {
    if (message.type() === 'error') {
      errors.push(message.text());
    }
  });
  return errors;
}

const routes = [
  {
    name: 'player',
    path: '/',
    ready: '#player',
    text: 'One More Time',
  },
  {
    name: 'library',
    path: '/#/library',
    ready: '#library',
    text: 'Discovery',
  },
  {
    name: 'cards',
    path: '/#/cards',
    ready: '#cards',
    text: '0001234567',
  },
  {
    name: 'settings',
    path: '/#/settings',
    ready: '#settings',
    text: '192.168.1.42',
  },
];

for (const route of routes) {
  test(`${route.name} route renders`, async ({ page }) => {
    const consoleErrors = collectConsoleErrors(page);
    await mockBackend(page);
    await page.goto(route.path);
    await expect(page.locator(route.ready)).toBeVisible();
    await expect(page.getByText(route.text, { exact: false }).first()).toBeVisible();
    await expectStableLayout(page);
    if (route.name === 'library') {
      await expectAbove(
        page.getByRole('switch', { name: 'Toggle Album/Folder view' }),
        page.getByText('Discovery', { exact: true }),
      );
    }
    if (route.name === 'cards') {
      await expectAbove(
        page.getByRole('heading', { name: 'Cards' }),
        page.getByText('0001234567', { exact: true }),
      );
    }
    await expect(page).toHaveScreenshot(`${route.name}.png`);
    expect(consoleErrors).toEqual([]);
  });
}

test('bottom navigation changes routes', async ({ page }) => {
  const consoleErrors = collectConsoleErrors(page);
  await mockBackend(page);
  await page.goto('/');

  await page.getByRole('link', { name: 'Library' }).click();
  await expect(page).toHaveURL(/#\/library\/albums$/);

  await page.getByRole('link', { name: 'Cards' }).click();
  await expect(page).toHaveURL(/#\/cards$/);

  await page.getByRole('link', { name: 'Settings' }).click();
  await expect(page).toHaveURL(/#\/settings$/);
  expect(consoleErrors).toEqual([]);
});

test('player backdrop covers its full width across the md breakpoint', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== 'desktop');
  const consoleErrors = collectConsoleErrors(page);
  await page.setViewportSize({ width: 800, height: 800 });
  await mockBackend(page, { showCovers: true });
  await page.goto('/');

  await expect(page.locator('#player img')).toBeVisible();
  for (const width of [800, 899, 900]) {
    await page.setViewportSize({ width, height: 800 });
    const [playerBox, backdropBox] = await Promise.all([
      page.locator('#player').boundingBox(),
      page.getByTestId('player-backdrop').boundingBox(),
    ]);

    expect(backdropBox.x).toBeCloseTo(playerBox.x, 0);
    expect(backdropBox.width).toBeCloseTo(playerBox.width, 0);
    expect(playerBox.width).toBeCloseTo(width < 900 ? width : width / 2, 0);
  }

  await page.setViewportSize({ width: 899, height: 800 });
  await expect(page).toHaveScreenshot('player-899.png');
  expect(consoleErrors).toEqual([]);
});

test('encoded library folder routes preserve the folder path', async ({ page }) => {
  const consoleErrors = collectConsoleErrors(page);
  const { libraryCalls } = await mockBackend(page);
  await page.goto('/#/library/folders/Music%2FRock');

  await expect.poll(() => libraryCalls).toContain('Music/Rock');
  await expect(page.getByRole('link', { name: 'Library' })).toHaveClass(/Mui-selected/);
  await expect(page.getByText('sample.mp3')).toBeVisible();
  await expectStableLayout(page);
  expect(consoleErrors).toEqual([]);
});

test('library view toggle replaces the current nested route', async ({ page }) => {
  const consoleErrors = collectConsoleErrors(page);
  await mockBackend(page);
  await page.goto('/#/library/folders/Music%2FRock?cardId=123');

  await page.getByRole('switch', { name: 'Toggle Album/Folder view' }).click();

  await expect(page).toHaveURL(/#\/library\/albums\?cardId=123$/);
  await expect(page.getByText('Discovery', { exact: true })).toBeVisible();
  expect(consoleErrors).toEqual([]);
});

test('cards route shows its loading state while RPC is pending', async ({ page }) => {
  const consoleErrors = collectConsoleErrors(page);
  let releaseRpc;
  const rpcGate = new Promise(resolve => {
    releaseRpc = resolve;
  });

  await mockBackend(page, { rpcGate });
  await page.goto('/#/cards');

  await expect(page.getByRole('progressbar')).toBeVisible();
  releaseRpc();
  await expect(page.getByText('0001234567')).toBeVisible();
  expect(consoleErrors).toEqual([]);
});

test('RPC failures leave navigation and an error state available', async ({ page }) => {
  await mockBackend(page, { failRpc: true });
  await page.goto('/#/cards');

  await expect(page.getByText('An error occurred while loading cards list.')).toBeVisible();
  await expect(page.getByRole('link', { name: 'Settings' })).toBeVisible();
  await expectStableLayout(page);
});
