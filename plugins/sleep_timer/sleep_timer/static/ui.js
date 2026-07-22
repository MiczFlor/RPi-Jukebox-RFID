// Sleep timer UI extension for the Jukebox player webview.
//
// Contract (see documentation/developers/webui-plugins.md): this module exports mount(container, sdk)
// and unmount(container). No build step, no framework dependency (in particular, no React) -- the host
// webapp loads this file via a dynamic import() at runtime, so it must not assume any bundler is present.
// `sdk.call(package, plugin, method, kwargs)` is the only thing the host provides; it performs the RPC
// call the same way the webapp's own UI does internally.

const STEPS_MINUTES = [5, 10, 15, 20, 30, 45, 60, 90];

function formatRemaining(seconds) {
  const total = Math.max(0, Math.round(seconds));
  const minutes = Math.floor(total / 60);
  const rest = total % 60;
  return `${minutes}:${String(rest).padStart(2, '0')}`;
}

export function mount(container, sdk) {
  const state = { enabled: false, remaining: 0, minutes: STEPS_MINUTES[2], intervalId: null };

  const wrapper = document.createElement('div');
  wrapper.style.display = 'flex';
  wrapper.style.alignItems = 'center';
  wrapper.style.gap = '8px';
  wrapper.style.marginTop = '8px';
  wrapper.style.fontFamily = 'inherit';
  wrapper.style.color = 'inherit';

  const label = document.createElement('span');
  label.textContent = 'Sleep timer';
  label.style.opacity = '0.7';
  label.style.fontSize = '0.875rem';

  const select = document.createElement('select');
  STEPS_MINUTES.forEach((minutes) => {
    const option = document.createElement('option');
    option.value = String(minutes);
    option.textContent = `${minutes} min`;
    select.appendChild(option);
  });
  select.value = String(state.minutes);
  select.onchange = () => {
    state.minutes = Number(select.value);
  };

  const button = document.createElement('button');
  button.type = 'button';

  const countdown = document.createElement('span');
  countdown.style.fontVariantNumeric = 'tabular-nums';

  const render = () => {
    button.textContent = state.enabled ? 'Cancel' : 'Start';
    select.style.display = state.enabled ? 'none' : '';
    countdown.textContent = state.enabled ? formatRemaining(state.remaining) : '';
  };

  const tick = () => {
    if (!state.enabled) return;
    state.remaining = Math.max(0, state.remaining - 1);
    if (state.remaining <= 0) {
      state.enabled = false;
    }
    render();
  };

  const refresh = async () => {
    try {
      const result = await sdk.call('sleep_timer', 'get_state', null, {});
      state.enabled = !!(result && result.enabled);
      state.remaining = (result && result.remaining_seconds) || 0;
      render();
    } catch (error) {
      console.error('[sleep_timer] Failed to fetch state:', error);
    }
  };

  button.onclick = async () => {
    try {
      if (state.enabled) {
        await sdk.call('sleep_timer', 'cancel', null, {});
        state.enabled = false;
      } else {
        await sdk.call('sleep_timer', 'start', null, { wait_seconds: state.minutes * 60 });
        state.enabled = true;
        state.remaining = state.minutes * 60;
      }
      render();
    } catch (error) {
      console.error('[sleep_timer] Failed to start/cancel timer:', error);
    }
  };

  wrapper.appendChild(label);
  wrapper.appendChild(select);
  wrapper.appendChild(button);
  wrapper.appendChild(countdown);
  container.appendChild(wrapper);

  render();
  refresh();
  state.intervalId = setInterval(tick, 1000);

  container.__sleepTimerCleanup = () => clearInterval(state.intervalId);
}

export function unmount(container) {
  if (container.__sleepTimerCleanup) {
    container.__sleepTimerCleanup();
    delete container.__sleepTimerCleanup;
  }
}
