# Plugin System: Where We Are, Why It's Worth It, and How to Try It

This is the entry point if you want to evaluate the new plugin architecture -- what it is, why it's an
improvement, and how to run it yourself in the next few minutes. For the full backlog, open questions, and
the (much larger, separate) packaging/installation overhaul this connects to, see the
[Roadmap: Plugin Architecture & Packaging](./roadmap-plugins-and-packaging.md).

## The problem this solves

Today, everything that extends the Jukebox -- core components and third-party additions alike -- has to
live inside this repository and gets wired up through a single, hand-maintained YAML mapping
(`modules.named` in `jukebox.yaml`) of arbitrary name-to-module-path strings. There's no real package
boundary: adding something means editing this repo's source tree directly, there's no way to install an
extension independently, and nothing stops a typo in the YAML from silently breaking startup. Optional
hardware backends (MQTT, battery monitors, event devices) already show the pain: they're only reachable by
hand-editing a module path string that has to be *exactly* right, undocumented anywhere the type checker
or IDE could help.

A plugin author also has no way to add UI for their feature -- any widget requires editing the webapp's own
source, `src/webapp/src/commands/index.js` and a new component wired into an existing page. There is no
extension point on the frontend at all today.

## What's been built

* **A real Python package.** `src/jukebox/pyproject.toml` makes the core app installable via standard
  tooling (`pip`/`uv`) for the first time, instead of only running via `cd src/jukebox && python
  run_jukebox.py`.
* **Two-tier plugin loading, both strictly opt-in.** Core components (shipped in `src/jukebox/components`)
  are selected via an explicit `components` list in `jukebox.yaml`, in a fixed, dependency-respecting load
  order. User plugins -- independently installable packages, via `pip`/`uv`, not living in this repo at all
  -- are discovered through the standard `jukebox.plugins` Python entry-point mechanism and activated via a
  `plugins` list. Installing a plugin package doesn't silently activate it; the system also tells you when
  something is installed but not yet turned on.
* **Plugins can ship their own webapp UI**, with zero changes to the webapp's source. A plugin declares
  which UI "slot" it extends and ships a small static JS bundle; a new core component
  (`components.webui_plugins`) serves it and reports it to the frontend, which loads it at runtime via a
  generic `<PluginSlot name="..."/>` component. See
  [Webapp UI Plugins](./webui-plugins.md) for the full contract.
* **Modern dev tooling**, introduced via `uv`: `ruff` for linting and formatting (replacing `flake8`) and
  `pyright` for type checking, both zero-install (`uv run ...` fetches them on demand).
* **Test coverage** for the plugin loading path itself (`test/plugs`, `test/webui_plugins`) -- opt-in
  activation, load order, error handling, manifest building -- not just manual spot-checks.

## Proof, not just a proposal: the `sleep_timer` plugin

[`plugins/sleep_timer`](../../plugins/sleep_timer) is a complete, working plugin built entirely outside
`src/jukebox/components` -- a sleep timer for the player view (stop playback after N minutes, handy for
kids listening to audiobooks at bedtime). It exercises every part of the new system in one real feature:

* Backend logic loaded via a `jukebox.plugins` entry point, not core repo code.
* Its own configuration, read through the same shared config mechanism core components use -- nothing
  plugin-specific needed there.
* Its own webapp widget (`plugins/sleep_timer/sleep_timer/static/ui.js`), rendered in the player view
  without a single line changed in `src/webapp`.
* Reuses existing core functionality (`timers.timer_stop_player`) rather than duplicating it -- plugins can
  build on top of the core app, not just next to it.

This was built, and has since been run end-to-end in a real container (see below) -- it isn't a paper
design.

## Why it's worth adopting

* **Third-party/community extensions become possible without forking core.** A plugin is a normal,
  independently versioned Python package.
* **No more editing the webapp to add a feature's UI.** The `PluginSlot` mechanism is the one thing the
  core webapp needed to add; everything plugin-specific stays in the plugin.
* **Explicit and auditable.** Both core components and user plugins require an explicit name in
  `jukebox.yaml` to load -- nothing activates just because it's installed.
* **Standard packaging instead of ad-hoc YAML string mapping.** Dependencies, versions, and entry points
  are declared where the Python ecosystem already expects them, which is also what makes tooling like
  `uv`, `ruff`, and `pyright` applicable at all.
* **It's tested**, both with unit tests and by actually running it (a real bug -- two threads racing to
  start the same event loop -- was only found by running the container, not by reasoning about the code;
  see the roadmap doc's history for details).

## Try it yourself

Both paths install `plugins/sleep_timer` alongside the core app so you have a real feature to click on, not
just a log message. Given a choice, do the Docker path first -- it's faster and needs no Pi hardware.

### 1. Docker (fast, no Pi hardware needed)

Follow [Docker Development Runbook](./docker.md) for host-specific prerequisites (Mac/Linux/Windows,
Pulseaudio setup), then, from the repo root:

```bash
docker build -f docker/Dockerfile.libzmq -t libzmq:local .
docker-compose -f docker/docker-compose.yml build
docker-compose -f docker/docker-compose.yml up
```

`docker/Dockerfile.jukebox` now installs both the core package and `plugins/sleep_timer` via `uv`. Once
it's up, the sleep timer widget shows up in the player view of the webapp
(default: `http://localhost:3000`).

### 2. A real Raspberry Pi (the final validation step)

Follow [Installation](../builders/installation.md) as usual. `installation/routines/setup_jukebox_core.sh`
now also installs the `rpi-jukebox-rfid` package (via `uv`, from the local checkout -- see the roadmap doc
for why this is a workaround until a PyPI release exists). To also get the sleep timer plugin, install it
the same way once the base installation is done:

```bash
source ~/RPi-Jukebox-RFID/.venv/bin/activate
uv pip install --no-deps -e ~/RPi-Jukebox-RFID/plugins/sleep_timer
```

then add `sleep_timer` to the `plugins` list in `~/RPi-Jukebox-RFID/shared/settings/jukebox.yaml` (already
the default if you're installing from this branch) and restart the `jukebox-daemon` service.

## Known limitations, right now

* The webapp UI contract for plugins is plain JS/DOM, not React/MUI -- deliberate, to avoid every plugin
  needing its own copy of React (see [Webapp UI Plugins](./webui-plugins.md#current-limitations-proof-of-concept)).
  Only one slot (`player`) exists so far.
* One core component (`battmon`/battery monitor) doesn't fit the current "one name -> one module" model
  because it has multiple mutually exclusive hardware backends -- documented as an open gap, not solved.
* No formatting baseline commit yet (`ruff format` would touch ~5300 lines the first time it's applied),
  and pyright reports ~340 pre-existing type errors on code that's never been type-checked before -- both
  deliberately deferred, not blocking anything.

None of the above blocks trying the system out; they're scoped and tracked in the
[roadmap doc](./roadmap-plugins-and-packaging.md), along with everything about the (separate, much bigger,
not-yet-started) effort to eventually install the Jukebox without a git checkout at all.
