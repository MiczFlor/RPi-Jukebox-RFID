# Installing Phoniebox future3

Welcome! This guide walks you through installing Phoniebox future3 on a Raspberry Pi running **Raspberry Pi OS Lite**.

There are two ways to run the installation:

* **Interactive** — the classic one-line installer that asks a few questions during setup (see [Install Phoniebox software](#install-phoniebox-software)).
* **Non-interactive (headless)** — the same installer, driven by a flat `KEY=VALUE` config file or environment variables, without any prompts. Ideal for automated and scripted installations (see [Non-Interactive Installation](#non-interactive-installation)).

Both modes install the same software; they only differ in how the installation options are supplied.

## Install Raspberry Pi OS Lite

> [!IMPORTANT]
> All Raspberry Pi models are supported. For sufficient performance, **we recommend Pi 2, 3 or Zero 2** (`ARMv7` models). Because Pi 1 or Zero 1 (`ARMv6` models) have limited resources, they are slower (during installation and start up procedure) and might require a bit more work! Pi 4 and 5 are an excess ;-)

Before you can install the Phoniebox software, you need to prepare your Raspberry Pi.

This instruction uses the official [Raspberry Pi Imager](https://www.raspberrypi.com/software/). We recommend using the latest **Raspberry Pi OS Lite** image - Trixie.

### Raspberry Pi Imager

1. Connect a Micro SD card to your computer (preferable an SD card with high read throughput)
1. Start the Raspberry Pi Imager
1. Model: select "No filtering"
1. OS: select **Raspberry Pi OS (other)** and then **Raspberry Pi OS Lite** (64 bit, 32 bit should also work) - the version without Desktop environment
1. Storage: Select your Micro SD card (your card will be formatted)
1. Customize:
    * Hostname: choose hostname for the network (e.g. "phoniebox")
    * Localization: choose according to your location
    * User: choose a username and a password
    * Wifi: provide your wifi settings
    * Remote: enable SSH with "Use password authentication"
1. Click `Write`
1. Confirm the next warning about erasing the SD card with `Yes`
1. Wait for the imaging process to be finished (it'll take a few minutes)
1. Plug the SD into your Pi and optionally connect keyboard, monitor and mouse.

## Install Phoniebox software

Choose the Phoniebox version you want to install, then choose how to run the installation. Every version can be installed either **interactively** (the installer asks a few questions during setup) or **non-interactively** (headless: all options are supplied via a config file or environment variables). Both modes install the same software — they only differ in how the installation options are provided.

* [Stable Release](#stable-release)
* [Pre-Release](#pre-release)
* [Development](#development)

Each version below shows the interactive one-liner and the non-interactive variant. All non-interactive details (config file, environment variables, all available options) are described in [Non-Interactive Installation](#non-interactive-installation).

After a successful installation, [configure your Phoniebox](configuration.md).

> [!TIP]
> Depending on your hardware, this installation might last around 60 minutes (usually it's faster, 20-30 min). It refreshes the package index, installs Phoniebox dependencies and applies settings. Be patient and don't let your computer go to sleep. It might disconnect your SSH connection causing the interruption of the installation process. Consider starting the installation in a terminal multiplexer like 'screen' or 'tmux' to avoid this.

The Web App can upload files or complete folder trees, organize the audio
library, and delete files or folders, so Samba is disabled by default during
installation. Choose Samba when you also want direct network access to the
complete `shared` directory, including configuration files. See
[Samba](samba.md) for details.

Current Raspberry Pi OS images normally do not need a full operating system upgrade immediately after imaging, so the installer skips it by default. To opt in to `apt-get full-upgrade` and `autoremove`, prefix an installation command with:

```bash
UPDATE_RASPI_OS=true
```

### Stable Release

This will install the latest **stable release** from the *future3/main* branch.

Run it **interactively** — the installer asks a few questions during setup:

```bash
cd; bash <(wget -qO- https://raw.githubusercontent.com/MiczFlor/RPi-Jukebox-RFID/future3/main/installation/install-jukebox.sh)
```

Or **non-interactively** — all options come from a config file:

```bash
cd; bash <(wget -qO- https://raw.githubusercontent.com/MiczFlor/RPi-Jukebox-RFID/future3/main/installation/install-jukebox.sh) --config "$HOME/install_config.env"
```

### Pre-Release

This will install the latest **pre-release** from the *future3/develop* branch.

Run it **interactively**:

```bash
cd; GIT_BRANCH='future3/develop' bash <(wget -qO- https://raw.githubusercontent.com/MiczFlor/RPi-Jukebox-RFID/future3/develop/installation/install-jukebox.sh)
```

Or **non-interactively** — the branch is supplied as an environment variable alongside the config file:

```bash
cd; GIT_BRANCH='future3/develop' bash <(wget -qO- https://raw.githubusercontent.com/MiczFlor/RPi-Jukebox-RFID/future3/develop/installation/install-jukebox.sh) --config "$HOME/install_config.env"
```

### Development

You can also install a specific branch and/or a fork repository. Update the variables to refer to your desired location. (The URL must not necessarily be updated, unless you have actually updated the file being downloaded.)

> [!IMPORTANT]
> A fork repository must be named '*RPi-Jukebox-RFID*' like the official
> repository.

Run it **interactively**:

```bash
cd; GIT_USER='your-github-user' GIT_BRANCH='feature/my-change' bash <(wget -qO- https://raw.githubusercontent.com/MiczFlor/RPi-Jukebox-RFID/future3/develop/installation/install-jukebox.sh)
```

Or **non-interactively** — the branch and fork variables work in both modes:

```bash
cd; GIT_USER='your-github-user' GIT_BRANCH='feature/my-change' bash <(wget -qO- https://raw.githubusercontent.com/MiczFlor/RPi-Jukebox-RFID/future3/develop/installation/install-jukebox.sh) --config "$HOME/install_config.env"
```

The installer uses HTTPS and fetches only the selected branch with shallow history. Set `GIT_USE_SSH=true` to opt in to SSH access. The installed checkout remains a normal tracking branch, so `git pull` works as usual.

Developers who later need all branches, history and tags can fetch them explicitly:

```bash
git fetch --unshallow origin
git fetch origin --tags
```

> [!NOTE]
> The installer deploys a pre-built Web App bundle matching the exact checked-out commit.
> It never compiles the Web App on the Raspberry Pi and never falls back to a bundle from another commit. If a bundle is unavailable, publish or rerun the Web App CI workflow for that commit before retrying the installation. See the developers [Web App](../developers/webapp.md) documentation for details.

### Non-Interactive Installation

The commands in the [Stable Release](#stable-release), [Pre-Release](#pre-release) and [Development](#development) sections show the non-interactive variant for every version. This section describes that mode in detail: all options are supplied either as environment variables or through a flat `KEY=VALUE` config file passed with `--config <file>`, so the installer runs **without any interactive prompts**. This is ideal for automated and scripted installations.

> [!NOTE]
> Behavior in non-interactive mode:
>
> * An existing installation does **not** abort the installer. It is backed up (`EXISTING_INSTALL_ACTION=backup`, the default) or removed (`EXISTING_INSTALL_ACTION=remove`) first.
> * The welcome and the final reboot prompts are skipped. The calling process is responsible for rebooting the Pi afterwards (e.g. `sudo reboot`).
> * If `ENABLE_RFID_READER=true` (the default), you **must** set `RFID_READER_MODULE` to one of the supported reader modules, otherwise the installer aborts.
> * Readers that normally ask for device/pin selection (e.g. `generic_usb`, `generic_nfcpy`, `rc522_spi`) are configured **without any prompts** in non-interactive mode: `rc522_spi` uses the default wiring, `generic_usb`/`generic_nfcpy` auto-detect a uniquely connected device. If no unique device can be determined, the installer aborts with a clear message — provide the missing values with `RFID_READER_PARAMS` (e.g. `device_name=...` or `spi_ce=0;pin_irq=24`) to configure such a reader without any prompts.
>

#### Config file

The config file is a simple `KEY=VALUE` file — no YAML parser is needed on the Pi. Create it on your computer and copy it to the Pi, or create it directly in your SSH session:

```bash
cd
cat > install_config.env <<'EOF'
GIT_USER=MiczFlor
GIT_BRANCH=future3/main
ENABLE_STATIC_IP=false
DISABLE_IPv6=true
ENABLE_AUTOHOTSPOT=false
DISABLE_BLUETOOTH=true
DISABLE_ONBOARD_AUDIO=true
ENABLE_RFID_READER=true
RFID_READER_MODULE=pn532_i2c_py532
ENABLE_SAMBA=false
ENABLE_WEBAPP=true
ENABLE_KIOSK_MODE=false
UPDATE_RASPI_OS=false
EXISTING_INSTALL_ACTION=backup
EOF
```

Run the installer with the config file (`--config` implies non-interactive mode):

```bash
cd; bash <(wget -qO- https://raw.githubusercontent.com/MiczFlor/RPi-Jukebox-RFID/future3/main/installation/install-jukebox.sh) --config "$HOME/install_config.env"
```

Alternatively, pass the options as environment variables and enable non-interactive mode with the `--non-interactive` flag:

```bash
cd; NON_INTERACTIVE=true ENABLE_RFID_READER=false bash <(wget -qO- https://raw.githubusercontent.com/MiczFlor/RPi-Jukebox-RFID/future3/main/installation/install-jukebox.sh)
```

#### RFID reader with configuration values

Readers that need device or pin values (e.g. `generic_nfcpy`, `generic_usb`, `rc522_spi`) receive them through `RFID_READER_PARAMS` — a `;`-separated list of `key=value` pairs. These values are written directly into the reader's `config` section of the generated `shared/settings/rfid.yaml`.

Besides the values, the non-interactive installer also takes care of each reader's **dependencies**: many reader modules ship their own Python packages (`requirements.txt`) and/or driver & system setup (`setup.inc.sh`). By default (`RFID_READER_DEPS=auto`) the installer installs them automatically, exactly like the interactive flow would after confirmation — e.g. for `generic_nfcpy` it installs the `nfcpy` Python package and applies the kernel/udev driver handling (so the reader is accessible without root), and for `rc522_spi` it installs the `pi-rc522` library and enables SPI. Set `RFID_READER_DEPS=no` to skip the dependency installation (e.g. because you manage them yourself). `RFID_READER_DEPS=query` is not allowed in non-interactive mode, because it would prompt for confirmation.

For example, a USB NFC reader (`generic_nfcpy`) identified by the vendor/product ID `usb:072f:2200`:

```bash
cd
cat > install_config.env <<'EOF'
GIT_USER=MiczFlor
GIT_BRANCH=future3/main
ENABLE_RFID_READER=true
RFID_READER_MODULE=generic_nfcpy
RFID_READER_PARAMS="device_path=usb:072f:2200"
ENABLE_SAMBA=false
ENABLE_WEBAPP=true
ENABLE_KIOSK_MODE=false
EXISTING_INSTALL_ACTION=backup
EOF

cd; bash <(wget -qO- https://raw.githubusercontent.com/MiczFlor/RPi-Jukebox-RFID/future3/main/installation/install-jukebox.sh) --config "$HOME/install_config.env"
```

This writes the following reader configuration to `shared/settings/rfid.yaml`:

```yaml
rfid:
  readers:
    read_00:
      module: generic_nfcpy
      config:
        device_path: usb:072f:2200
      same_id_delay: 1.0
      log_ignored_cards: false
      place_not_swipe:
        enabled: false
        card_removal_action:
          alias: pause
```

Other readers use the same mechanism, e.g. `generic_usb` with `RFID_READER_PARAMS="device_name=KKMoon USB Keyboard"` or `rc522_spi` with `RFID_READER_PARAMS="spi_ce=0;pin_irq=24"`.

> [!NOTE]
> Quote the value whenever it contains `;` or spaces (e.g. `RFID_READER_PARAMS="spi_ce=0;pin_irq=24"`), because the config file is a plain shell `KEY=VALUE` file that gets sourced.

#### Run from a local checkout

Developers who have the repository checked out can start the installer directly from the local copy instead of piping it from GitHub:

```bash
cd ~/RPi-Jukebox-RFID
bash installation/install-jukebox.sh --config ~/install_config.env
```

Environment-variable only variant:

```bash
cd ~/RPi-Jukebox-RFID
NON_INTERACTIVE=true ENABLE_RFID_READER=false bash installation/install-jukebox.sh
```

Install your own fork or feature branch:

```bash
cd ~/RPi-Jukebox-RFID
GIT_USER='your-github-user' GIT_BRANCH='feature/my-change' ENABLE_RFID_READER=false bash installation/install-jukebox.sh --non-interactive
```

> [!NOTE]
> The installer always downloads the installation source from GitHub for the configured `GIT_USER`/`GIT_BRANCH` and installs it to `~/RPi-Jukebox-RFID` — running the script from a local checkout does not change that. To test your own fork or feature branch, set `GIT_USER`/`GIT_BRANCH` accordingly (the changes must be pushed). This is the same flow the CI uses in `ci/installation/run_install_common.sh`.

#### Available options

Every option below is a plain shell variable. Values set via the config file or the environment are kept; anything unset falls back to the listed default.

| Variable | Default | Description |
| --- | --- | --- |
| `GIT_USER` | `MiczFlor` | GitHub user/organisation the source is downloaded from |
| `GIT_BRANCH` | `future3/main` | Branch to install |
| `GIT_USE_SSH` | `false` | Use SSH instead of HTTPS to fetch the source |
| `ENABLE_STATIC_IP` | `true` | Configure a static IP address |
| `DISABLE_IPv6` | `true` | Disable IPv6 |
| `ENABLE_AUTOHOTSPOT` | `false` | Enable the WiFi autohotspot fallback service |
| `AUTOHOTSPOT_PROFILE` | `Phoniebox_Hotspot` | Autohotspot profile name |
| `AUTOHOTSPOT_SSID` | profile name | Autohotspot SSID |
| `AUTOHOTSPOT_PASSWORD` | `PlayItLoud!` | Autohotspot password |
| `AUTOHOTSPOT_IP` | `10.0.0.1` | Autohotspot IP address |
| `AUTOHOTSPOT_COUNTRYCODE` | `DE` | Autohotspot WiFi country code |
| `DISABLE_BLUETOOTH` | `true` | Disable Bluetooth |
| `DISABLE_BOOT_SCREEN` | `true` | Disable the boot splash screen |
| `DISABLE_BOOT_LOGS_PRINT` | `true` | Disable boot log output |
| `SETUP_MPD` | `true` | Set up MPD (Music Player Daemon) |
| `ENABLE_MPD_OVERWRITE_INSTALL` | `true` | Overwrite an existing MPD configuration |
| `UPDATE_RASPI_OS` | `false` | Run `apt-get full-upgrade` and `autoremove` |
| `ENABLE_RFID_READER` | `true` | Set up an RFID reader |
| `RFID_READER_MODULE` | – | Reader module, e.g. `pn532_i2c_py532`, `mfrc522_i2c`, `rc522_spi`, `rdm6300_serial`, `generic_usb`, `generic_nfcpy` (required when `ENABLE_RFID_READER=true`) |
| `RFID_READER_PARAMS` | – | Reader parameters for non-interactive configuration, `key=value` pairs separated by `;` (e.g. `device_path=usb:072f:2200` for `generic_nfcpy`). Only needed for readers that cannot determine a unique default automatically — see [RFID reader with configuration values](#rfid-reader-with-configuration-values). |
| `RFID_READER_DEPS` | `auto` | Install the reader's Python packages (`requirements.txt`) and driver/system setup (`setup.inc.sh`): `auto` (default) installs them, `no` skips them. `query` is not allowed in non-interactive mode (it would prompt). |
| `ENABLE_SAMBA` | `false` | Enable Samba network shares |
| `ENABLE_WEBAPP` | `true` | Install the Web App |
| `ENABLE_WEBAPP_PROD_DOWNLOAD` | `release-only` | Web App bundle download mode (`true` or `release-only`) |
| `ENABLE_KIOSK_MODE` | `false` | Launch the Web App in kiosk mode on boot |
| `DISABLE_ONBOARD_AUDIO` | `false` | Disable the Pi's on-chip audio (recommended with external sound cards) |
| `HIFIBERRY_BOARD` | – | HiFiBerry HAT to enable, e.g. `hifiberry-dac`, `hifiberry-dacplus` |
| `EXISTING_INSTALL_ACTION` | `backup` | Handling of an existing installation: `backup` or `remove` |

The installer prints the log file path to the console (e.g. `INSTALLATION_LOGFILE=/home/pi/INSTALL-1234567890.log`) so a calling process can follow the installation live — see [Logs](#logs) below.

### Logs

To follow the installation closely, use this command in another terminal.

```bash
cd; tail -f INSTALL-<fullname>.log
```
