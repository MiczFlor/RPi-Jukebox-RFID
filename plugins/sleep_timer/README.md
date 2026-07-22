# jukebox-plugin-sleep-timer

Example/reference user plugin for the Jukebox: adds a sleep timer to the player webview that stops
playback after a chosen duration (handy for kids listening to audiobooks at bedtime).

Demonstrates both parts of the Jukebox plugin system:

* a backend plugin loaded via the `jukebox.plugins` entry-point group (see
  `documentation/developers/docstring/README.md#jukebox.plugs`), and
* a self-contained webapp UI extension that ships with the plugin instead of requiring changes to the
  webapp's own source (see `documentation/developers/webui-plugins.md`).

## Install

```bash
uv pip install -e plugins/sleep_timer
```

Then in `jukebox.yaml`, make sure `webui_plugins` is enabled under `components` and add `sleep_timer` to
`plugins` (both are already the default in `resources/default-settings/jukebox.default.yaml`).
