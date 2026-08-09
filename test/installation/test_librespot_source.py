import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).parents[2]
SETUP = ROOT / 'installation' / 'routines' / 'setup_spotify.sh'
PREPARE_DEPENDENCIES = (
    ROOT / 'installation' / 'routines' / 'prepare_dependencies.sh'
)
DOCKERFILE = ROOT / 'docker' / 'Dockerfile.librespot'
BUILD_DOCKERFILE = ROOT / 'docker' / 'Dockerfile.librespot-build'
DEFAULTS = ROOT / 'installation' / 'includes' / '01_default_config.sh'
OPTIONS = ROOT / 'installation' / 'routines' / 'customize_options.sh'
OPTIMIZE_BOOT = ROOT / 'installation' / 'routines' / 'optimize_boot_time.sh'
WEBAPP_SETUP = ROOT / 'installation' / 'routines' / 'setup_jukebox_webapp.sh'


def _revision(contents, pattern):
    match = re.search(pattern, contents, flags=re.MULTILINE)
    assert match is not None
    return match.group(1)


def _run_install_function(home_path, cargo_status):
    harness = r'''
HOME_PATH="$1"
SETUP_PATH="$2"
CARGO_STATUS="$3"
INSTALLATION_PATH="$(dirname "$(dirname "$(dirname "${SETUP_PATH}")")")"

print_lc() {
    :
}

cargo() {
    printf '%s\n%s\n' "${TMPDIR}" "${CARGO_HOME}" \
        > "${HOME_PATH}/cargo-paths"
    return "${CARGO_STATUS}"
}

exit_on_error() {
    printf '%s' "$1" > "${HOME_PATH}/installer-error"
    exit 42
}

source "${SETUP_PATH}"
_spotify_install_build_dependencies() {
    :
}
_spotify_cleanup_build_dependencies() {
    :
}
_spotify_install_librespot_from_source
'''
    return subprocess.run(
        [
            'bash',
            '-c',
            harness,
            'test-librespot-installer',
            str(home_path),
            str(SETUP),
            str(cargo_status),
        ],
        check=False,
        capture_output=True,
        text=True,
    )


def test_installer_and_docker_pin_the_same_librespot_revision():
    setup = SETUP.read_text()
    prepare_dependencies = PREPARE_DEPENDENCIES.read_text()
    build_dockerfile = BUILD_DOCKERFILE.read_text()
    runtime_dockerfile = DOCKERFILE.read_text()

    setup_revision = _revision(
        setup,
        r'^LIBRESPOT_REVISION="([0-9a-f]{40})"$',
    )
    docker_revision = _revision(
        build_dockerfile,
        r'^ARG LIBRESPOT_REV=([0-9a-f]{40})$',
    )

    assert setup_revision == docker_revision
    assert '--git "${LIBRESPOT_REPOSITORY}"' in setup
    assert '--rev "${LIBRESPOT_REVISION}"' in setup
    assert 'fetch --depth 1 origin "${LIBRESPOT_REV}"' in build_dockerfile
    assert 'rust:1.85-slim-bookworm' in build_dockerfile
    assert 'ARG LIBRESPOT_SOURCE_DATE_EPOCH=1775501277' in build_dockerfile
    assert 'SOURCE_DATE_EPOCH="${LIBRESPOT_SOURCE_DATE_EPOCH}"' in (
        build_dockerfile
    )
    assert 'cargo install' in build_dockerfile
    assert 'libpulse0' in runtime_dockerfile
    assert 'libssl3t64' in runtime_dockerfile
    assert 'cargo install' not in runtime_dockerfile
    assert 'cargo libpulse-dev libssl-dev pkg-config' not in prepare_dependencies


def test_installer_no_longer_offers_or_disables_ipv6():
    assert 'DISABLE_IPv6' not in DEFAULTS.read_text()
    assert '_option_ipv6' not in OPTIONS.read_text()
    assert 'ipv6.disable=1' not in OPTIMIZE_BOOT.read_text()
    assert 'DISABLE_IPv6' not in WEBAPP_SETUP.read_text()


def test_spotify_removes_legacy_ipv6_disable_kernel_option(tmp_path):
    cmdline = tmp_path / 'cmdline.txt'
    cmdline.write_text(
        'console=serial0,115200 ipv6.disable=1 rootwait quiet\n',
    )
    harness = r'''
CMDLINE="$1"
SETUP_PATH="$2"

get_boot_cmdline_path() {
    printf '%s\n' "${CMDLINE}"
}
print_lc() {
    :
}
sudo() {
    "$@"
}
exit_on_error() {
    exit 42
}

source "${SETUP_PATH}"
_spotify_enable_ipv6
'''
    result = subprocess.run(
        [
            'bash',
            '-c',
            harness,
            'test-enable-ipv6',
            str(cmdline),
            str(SETUP),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert cmdline.read_text() == (
        'console=serial0,115200 rootwait quiet\n'
    )


def test_installer_builds_outside_system_tmp_and_cleans_up(tmp_path):
    result = _run_install_function(tmp_path, cargo_status=0)

    assert result.returncode == 0, result.stderr
    cargo_tmp, cargo_home = (tmp_path / 'cargo-paths').read_text().splitlines()
    cargo_tmp_dir = Path(cargo_tmp)
    assert cargo_tmp_dir.parent == tmp_path / '.cache'
    assert cargo_tmp_dir.name.startswith('librespot-build.')
    assert Path(cargo_home) == cargo_tmp_dir / 'cargo-home'
    assert not cargo_tmp_dir.exists()
    assert not (tmp_path / 'installer-error').exists()


def test_installer_cleans_up_and_aborts_when_cargo_fails(tmp_path):
    result = _run_install_function(tmp_path, cargo_status=1)

    assert result.returncode == 42
    cargo_tmp_dir = Path(
        (tmp_path / 'cargo-paths').read_text().splitlines()[0],
    )
    assert not cargo_tmp_dir.exists()
    assert (tmp_path / 'installer-error').read_text() == (
        'Failed to compile and install librespot.'
    )


def test_installer_tracks_only_build_dependencies_it_introduces(tmp_path):
    commands = tmp_path / 'commands'
    packages_to_remove = tmp_path / 'packages-to-remove'
    harness = r'''
SETUP_PATH="$1"
COMMANDS_PATH="$2"
PACKAGES_PATH="$3"

print_lc() {
    :
}

dpkg-query() {
    local package
    for package in "$@"; do
        :
    done
    case "${package}" in
        cargo|libssl-dev)
            return 1
            ;;
        *)
            printf '%s\n' "install ok installed"
            ;;
    esac
}

sudo() {
    printf '%s\n' "$*" >> "${COMMANDS_PATH}"
}

exit_on_error() {
    exit 42
}

source "${SETUP_PATH}"
_spotify_install_build_dependencies
printf '%s\n' "${LIBRESPOT_BUILD_DEPENDENCIES_TO_REMOVE[@]}" \
    > "${PACKAGES_PATH}"
'''
    result = subprocess.run(
        [
            'bash',
            '-c',
            harness,
            'test-librespot-dependencies',
            str(SETUP),
            str(commands),
            str(packages_to_remove),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert packages_to_remove.read_text().splitlines() == [
        'cargo',
        'libssl-dev',
    ]
    assert commands.read_text().splitlines() == [
        (
            'apt-get -y install --no-install-recommends '
            'cargo libpulse-dev libssl-dev pkg-config'
        ),
    ]


def test_cleanup_preserves_runtime_libraries_and_removes_build_chain(tmp_path):
    commands = tmp_path / 'commands'
    harness = r'''
SETUP_PATH="$1"
COMMANDS_PATH="$2"

print_lc() {
    :
}

sudo() {
    printf '%s\n' "$*" >> "${COMMANDS_PATH}"
}

source "${SETUP_PATH}"
LIBRESPOT_BUILD_DEPENDENCIES_TO_REMOVE=(cargo libssl-dev)
_spotify_runtime_package_owners() {
    printf '%s\n' libssl3t64:arm64 libpulse0:arm64
}
_spotify_cleanup_build_dependencies
'''
    result = subprocess.run(
        [
            'bash',
            '-c',
            harness,
            'test-librespot-cleanup',
            str(SETUP),
            str(commands),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert commands.read_text().splitlines() == [
        'apt-mark manual libpulse0:arm64 libssl3t64:arm64',
        'apt-get -y purge cargo libssl-dev',
        'apt-get -y autoremove --purge',
    ]


def test_source_build_is_only_used_when_explicitly_enabled(tmp_path):
    marker = tmp_path / 'source-build'
    harness = r'''
HOME_PATH="$1"
SETUP_PATH="$2"
MARKER="$3"
INSTALLATION_PATH="$(dirname "$(dirname "$(dirname "${SETUP_PATH}")")")"
GIT_USER=contributor
GIT_REPO_NAME=RPi-Jukebox-RFID

print_lc() {
    :
}

exit_on_error() {
    printf '%s' "$1" > "${HOME_PATH}/installer-error"
    exit 42
}

source "${SETUP_PATH}"
_spotify_install_prebuilt_librespot() {
    return 1
}
_spotify_install_librespot_from_source() {
    touch "${MARKER}"
}
_spotify_install_librespot
'''

    env = {'PATH': '/usr/bin:/bin', 'LIBRESPOT_ALLOW_SOURCE_BUILD': 'false'}
    result = subprocess.run(
        [
            'bash',
            '-c',
            harness,
            'test-librespot-source-fallback',
            str(tmp_path),
            str(SETUP),
            str(marker),
        ],
        check=False,
        capture_output=True,
        env=env,
        text=True,
    )

    assert result.returncode == 42
    assert not marker.exists()
    assert 'LIBRESPOT_ALLOW_SOURCE_BUILD=true' in (
        tmp_path / 'installer-error'
    ).read_text()

    env['LIBRESPOT_ALLOW_SOURCE_BUILD'] = 'true'
    (tmp_path / 'installer-error').unlink()
    result = subprocess.run(
        [
            'bash',
            '-c',
            harness,
            'test-librespot-source-fallback',
            str(tmp_path),
            str(SETUP),
            str(marker),
        ],
        check=False,
        capture_output=True,
        env=env,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert marker.exists()
    assert not (tmp_path / 'installer-error').exists()
