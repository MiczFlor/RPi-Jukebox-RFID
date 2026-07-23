# Roadmap: Plugin Architecture & Packaging/Installation

This tracks two related but independent efforts. Keep them separate when planning work: finishing one
does not require the other.

* **Track A — Plugin architecture**: how components and third-party plugins are loaded, configured, and
  (for the webapp) get their own UI. Mostly done as of this writing (proof of concept, real example
  plugin working end to end).
* **Track B — Installation/packaging overhaul**: how the Jukebox gets onto a Raspberry Pi in the first
  place. Discussion only so far, nothing implemented beyond one small touchpoint (see below).

## Track A: Plugin architecture

### Done

* Two-tier plugin loading in `jukebox.plugs` / `jukebox.daemon`:
  * **Core components** (shipped in `src/jukebox/components`): a fixed, hardcoded load order
    (`daemon.CORE_COMPONENTS`), selected via an explicit opt-in list, the `components` entry in
    `jukebox.yaml`. Order is not configurable -- only membership is.
  * **User plugins**: independently installed packages (`pip`/`uv`) advertising themselves under the
    `jukebox.plugins` entry-point group. Installing one does not activate it -- it must be listed in the
    `plugins` entry of `jukebox.yaml`, in the order it should load (unlike core components, load order
    here *is* config-controlled, since there's no other source of truth for third-party ordering).
  * Both are strictly opt-in: nothing loads without being named in the config.
* Feedback on load: `load_all_entry_points()` returns (and `daemon.py` logs + publishes as
  `core.plugins.inactive`) which installed user plugins are *not* activated, so it's discoverable rather
  than silent.
* Plugin configuration: works out of the box via the shared `jukebox.cfghandler` -- no special mechanism
  needed, a plugin just reads its own top-level key from `jukebox.yaml` like any core component does.
* Real packaging: `src/jukebox/pyproject.toml` (hatchling-based) makes the core app an installable Python
  package for the first time (previously it only ran via `cd src/jukebox && python run_jukebox.py`).
* Webapp UI extensions without core webapp changes: `components.webui_plugins` (scans loaded plugins for
  `PLUGIN_UI_SLOT`/`PLUGIN_UI_ENTRY`, serves each one's `static/` dir, exposes a `get_manifest()` RPC call)
  plus a generic `<PluginSlot name="..."/>` React component that dynamically `import()`s whatever the
  manifest reports. See `documentation/developers/webui-plugins.md` for the full contract.
* Worked example: `plugins/sleep_timer` -- a real, separately packaged user plugin exercising entry-point
  loading, config, RPC, *and* its own webapp UI (a vanilla-JS widget, no core webapp edits). Delegates to
  the pre-existing `timers.timer_stop_player` rather than re-implementing stop-after-timeout logic.
* Dev tooling: ruff (lint + format) and pyright (typecheck), both via `uv` (see root `pyproject.toml`,
  `package = false`, kept deliberately separate from `src/jukebox/pyproject.toml` so running them doesn't
  require building hardware-specific runtime dependencies like `rpi-lgpio`). Lint is a blocking CI gate;
  format-check and typecheck are `continue-on-error` for now (see "Known gaps").

### Known gaps / deliberately deferred

* **`battmon` (battery monitor) hardware variants**: three mutually exclusive backends
  (`batt_mon_i2c_ads1015` / `batt_mon_i2c_ina219` / `batt_mon_simulator`) share one fixed name, which
  doesn't fit the current "one name -> one module" catalog model. Currently requires a local code edit in
  `daemon.CORE_COMPONENTS` to pick a variant -- documented as a known gap in
  `documentation/builders/components/power/batterymonitor.md`, not solved.
* **No formatting baseline commit**: the codebase has never been run through a formatter; applying
  `ruff format` today would touch ~5300 lines across nearly every Python file. Deliberately not done yet
  -- needs its own dedicated commit and a moment when that's acceptable.
* **~340 pre-existing pyright errors** (basic mode): expected for code that's never been type-checked.
  Typecheck is report-only in CI until this backlog is worked down.
* **No automated test coverage** for the plugin loading path itself (entry points, `webui_plugins`,
  `PluginSlot`) -- only manually verified end-to-end during development.

### Does testing the plugin system require any of Track B?

No. Track A is self-contained: `uv pip install -e src/jukebox` (plus `-e plugins/sleep_timer` etc.) into
any environment -- a plain venv, the Docker dev setup, or a real Pi -- is enough to exercise entry-point
loading, config, RPC, and the webapp UI slot mechanism. None of it depends on how the Jukebox eventually
gets installed on a fresh Pi.

## Track B: Installation/packaging overhaul

### Goal (long-term, not started)

Replace the current git-checkout-as-runtime-location model with something closer to
`curl https://.../install.sh | sudo bash`, installing a real (eventually PyPI-published) Python package
instead of running scripts against a live git clone.

### Why this is a bigger undertaking than it sounds

The current installer (`installation/install-jukebox.sh` + `installation/routines/*.sh`) assumes the
running application *is* the git checkout:

* Config/resource paths are resolved relative to the script's own location (e.g. `run_jukebox.py`
  computes `../../shared/settings/jukebox.yaml` from `os.path.dirname(__file__)`), not from any
  installed-package-aware location. This breaks the moment the app runs from `site-packages` instead of a
  checkout -- **this is the biggest single blocker**, and touches nearly every component.
* The webapp's built static files, default settings/services/audio resources, and hardware-specific
  RFID/battery-monitor extras are all currently discovered via checkout-relative paths, not package data.
* Updates work via `git pull` -- to the point that even tarball ("release") downloads are converted into a
  real git repository during install just so this keeps working (see `installation/routines/setup_git.sh`).
  Removing the checkout needs a replacement update mechanism.

### Discussed (not prioritized) sub-steps

1. **Bundle the webapp as package data.** Build it first (the existing `.github/actions/build-webapp` /
   `bundle_webapp_and_release_v3.yml` already does this), then include the build output in the Python
   wheel (same `force-include` pattern already used for `plugins/sleep_timer/static/`) instead of
   downloading a separate tarball into the checkout. Serving (nginx config) needs to resolve the
   installed package's data path instead of `${INSTALLATION_PATH}/src/webapp/build`. Rough estimate: ~1
   day -- the hard parts (build pipeline, packaging pattern) already exist, this is mostly wiring.
2. **Resolve the core path problem.** Replace checkout-relative path resolution with something
   installation-location-independent (XDG-style config dirs, `importlib.resources` for package data,
   or similar). By far the largest piece -- affects nearly every module that currently does
   `../../shared/...` or `../../resources/...` path math.
3. **Ship resources (default settings/services/audio) as package data**, once (2) makes that
   meaningful.
4. **Turn hardware-specific extras (RFID readers, battery monitor variants) into optional-dependencies or
   separate plugins**, building on Track A's plugin mechanism.
5. **Replace the `git pull`-based update flow** with something that works for a pip/uv-installed package
   (e.g. `pip install --upgrade` plus a config/service migration step for anything installer-managed that
   changed).
6. **Build the actual curl-installer**, bundling or fetching the ~20 `installation/routines/*.sh` steps
   (Samba, autohotspot, kiosk mode, RFID setup, ...) without requiring a full git checkout first.
7. **Move parts of the install/update logic into the CLI tool** (today's `run_rpc_tool.py` /
   `jukebox-rpc-tool`, or a successor). Bash across ~20 loosely-coupled scripts makes error handling and
   especially system-update handling harder than it needs to be; a Python CLI could centralize this with
   proper error propagation, retries, and idempotency checks instead of shell-script conventions. Not
   fleshed out yet -- open how much of `installation/routines/*.sh` this would actually absorb vs. leaving
   as shell (OS package installs, hardware-specific setup like autohotspot/samba probably still make more
   sense as shell/apt).
8. **CLI tool as the plugin installer.** Rather than users running `uv pip install -e <path>` /
   `pip install <plugin>` by hand and then hand-editing `jukebox.yaml`'s `plugins` list, the CLI tool
   could offer a `jukebox plugin install <name>` (or similar) command that does both: installs the
   package (would need to expose something like a pip/uv-compatible interface itself -- installing into
   the right environment, handling the same dependency-resolution concerns) and registers it in the
   config. Depends on Track A's plugin mechanism (already there) and, loosely, on how packaging/updates
   are eventually handled here in Track B.

### Progress so far

* `installation/routines/setup_jukebox_core.sh` now also installs the `rpi-jukebox-rfid` package itself
  (via `uv pip install --no-deps -e`) from the local checkout, in addition to the existing
  `requirements.txt`-based dependency install. This is the *only* overlap between Track A and Track B so
  far: it makes the entry-point/console-script machinery from Track A actually usable on a real
  installed Pi, without pre-empting any Track B decisions. Marked as a `TODO`-workaround in the script,
  to be replaced by a plain `pip install rpi-jukebox-rfid` once published to PyPI.

### Open decisions

* Priority/order of the sub-steps above.
* Where the curl-installer would be hosted.
* Whether/how hardware variants become plugins vs. staying as installer-time choices.
* How much of the shell-script install/update logic moves into the CLI tool vs. stays as shell.
* What a plugin-installer interface in the CLI tool would need to expose (own pip/uv wrapper? shell out to
  `uv`? how does it interact with the `plugins` list in `jukebox.yaml`?).
