# Webapp UI Plugins

## Background

The Jukebox has a plugin system (see [Plugin Reference](./docstring/README.md#jukebox.plugs)) with two
kinds of plugins, both activated explicitly through `jukebox.yaml`:

* **Core plugins**, shipped inside `src/jukebox/components`, selected via the top-level `components` list.
* **User plugins**, independently installed python packages (e.g. via `pip`/`uv`) that advertise themselves
  under the `jukebox.plugins` entry-point group, selected via the top-level `plugins` list.

A plugin's *backend* logic (RPC-callable functions) works the same way regardless of which kind it is. Its
*frontend* is a different story: out of the box, a plugin has no way to show anything in the webapp -- the
webapp is a separately built React app that only knows about the UI code that was compiled into it. Adding
a widget for a plugin used to mean editing the webapp's own source (a new component, a new entry in
`src/webapp/src/commands/index.js`, wiring it into a parent component). That defeats the point of a
self-contained plugin: installing one shouldn't require patching the core webapp.

## The mechanism

A plugin can ship its own small UI bundle and have the webapp load it *at runtime*, with no core webapp
changes needed. Three pieces make this work:

1. **Convention**: a plugin package declares two module-level attributes in its `__init__.py`:

   ```python
   PLUGIN_UI_SLOT = 'player'    # which webapp UI slot to extend
   PLUGIN_UI_ENTRY = 'ui.js'    # entry point file, relative to a `static/` dir next to __init__.py
   ```

   and ships that entry point (plus anything else it needs) under a `static/` directory alongside its
   Python code.

2. **`components.webui_plugins`** (a core component, opt-in like any other -- add `webui_plugins` to the
   `components` list in `jukebox.yaml` to enable it): after all plugins have loaded, it scans every loaded
   plugin's module for the two attributes above, and for each one found:
   * serves that plugin's `static/` directory over a small dedicated HTTP server (config: `webui_plugins.host`
     / `webui_plugins.port`, default `localhost:5559`), and
   * exposes an RPC call, `webui_plugins.get_manifest`, returning `[{name, slot, url}, ...]` for every
     discovered UI extension.

3. **`PluginSlot`** (`src/webapp/src/components/general/PluginSlot.js`): the *one* generic piece added to
   the core webapp. `<PluginSlot name="player" />` fetches the manifest (via the `getUiPlugins` command),
   filters it by slot name, and for each match does a plain runtime `import()` of the plugin's `url`,
   mounting the result into its own `<div>`.

No plugin-specific code exists in the webapp; `PluginSlot` and the `webui_plugins` component are the only
things the core project maintains. Everything else -- the widget itself, its behaviour, its RPC calls --
lives entirely in the plugin package.

### The UI module contract

The file referenced by `PLUGIN_UI_ENTRY` must be loadable as a plain ES module (the webapp loads it with a
native, un-bundled `import()`, so it cannot assume webpack, React, or any other host dependency is
available to `import` from). It must export two functions:

```js
export function mount(container, sdk) {
  // container: an empty <div> created for this plugin instance
  // sdk.call(package, plugin, method, kwargs): performs the RPC call, exactly like the host's own UI does
}

export function unmount(container) {
  // clean up timers/listeners set up in mount()
}
```

Since no framework is provided, UI extensions are written in plain DOM APIs (`document.createElement`,
etc.). This keeps the contract dependency-free and avoids shipping (or worse, duplicating) React inside
every plugin bundle -- the tradeoff is that plugin authors don't get JSX/MUI for free.

## Worked example: `plugins/sleep_timer`

`plugins/sleep_timer` is a real user plugin exercising the whole mechanism end to end:

* `sleep_timer/__init__.py`: registers `start`/`cancel`/`get_state` (thin wrappers around the core
  `timers.timer_stop_player` timer) and declares `PLUGIN_UI_SLOT = 'player'`, `PLUGIN_UI_ENTRY = 'ui.js'`.
* `sleep_timer/static/ui.js`: a small vanilla-JS widget (duration dropdown, start/cancel button, countdown)
  implementing `mount`/`unmount`, calling `sdk.call('sleep_timer', 'start', null, { wait_seconds })` etc.
* `pyproject.toml`: declares the `jukebox.plugins` entry point; `static/` is picked up as package data
  automatically since it lives inside the declared `sleep_timer` package directory.

To try it: `uv pip install -e plugins/sleep_timer` into the same environment as the core package, add
`webui_plugins` to `components` and `sleep_timer` to `plugins` in `jukebox.yaml` (both already the default
in `resources/default-settings/jukebox.default.yaml`), and start the Jukebox -- the sleep timer widget
appears in the player view without a single line of webapp source having been touched for it.

## Current limitations (proof of concept)

* Only one slot exists today: `"player"` (rendered in `src/webapp/src/components/Player/index.js`). Adding
  further slots just means dropping another `<PluginSlot name="..." />` somewhere in the webapp.
* The static server started by `components.webui_plugins` has no authentication -- fine on a trusted LAN,
  not something to expose beyond that without further hardening.
* UI extensions are plain JS/DOM, not i18n-aware, and don't share the host's MUI theme.
