import hashlib
import io
import os
import subprocess
import tarfile
from pathlib import Path


ROOT = Path(__file__).parents[2]
SETUP = ROOT / 'installation' / 'routines' / 'setup_spotify.sh'
CHECKSUMS = ROOT / 'installation' / 'librespot-checksums.sha256'
DEFAULTS = ROOT / 'installation' / 'includes' / '01_default_config.sh'
OPTIONS = ROOT / 'installation' / 'routines' / 'customize_options.sh'
PREPARE_DEPENDENCIES = (
    ROOT / 'installation' / 'routines' / 'prepare_dependencies.sh'
)
BUILD_ID = '303026bb-phoniebox1'


def _archive(tmp_path, contents=b'#!/bin/sh\nexit 0\n'):
    archive = tmp_path / 'fixture.tar.gz'
    with tarfile.open(archive, 'w:gz') as bundle:
        binary = tarfile.TarInfo('librespot')
        binary.mode = 0o755
        binary.size = len(contents)
        bundle.addfile(binary, io.BytesIO(contents))

        license_contents = b'ISC license fixture\n'
        license_file = tarfile.TarInfo('LICENSE')
        license_file.mode = 0o644
        license_file.size = len(license_contents)
        bundle.addfile(license_file, io.BytesIO(license_contents))
    return archive


def _run_prebuilt_install(
    tmp_path,
    *,
    available_repository='contributor',
    checksum_matches=True,
    fixture=None,
):
    fixture = fixture or _archive(tmp_path)
    archive_name = f'librespot-{BUILD_ID}-linux-amd64.tar.gz'
    checksum = hashlib.sha256(fixture.read_bytes()).hexdigest()
    if not checksum_matches:
        checksum = '0' * 64
    checksums = tmp_path / 'checksums.sha256'
    checksums.write_text(f'{checksum}  {archive_name}\n')
    attempts = tmp_path / 'attempts'

    harness = r'''
HOME_PATH="$1"
SETUP_PATH="$2"
LIBRESPOT_CHECKSUMS_FILE="$3"
FIXTURE="$4"
ATTEMPTS="$5"
AVAILABLE_REPOSITORY="$6"
INSTALLATION_PATH="$(dirname "$(dirname "$(dirname "${SETUP_PATH}")")")"
GIT_USER=contributor
GIT_UPSTREAM_USER=MiczFlor
GIT_REPO_NAME=RPi-Jukebox-RFID
INSTALL_FUNCTION_CALLED="${HOME_PATH}/install-function-called"

print_lc() {
    :
}

log() {
    :
}

uname() {
    printf '%s\n' x86_64
}

validate_url() {
    printf '%s\n' "$1" >> "${ATTEMPTS}"
    [[ "$1" == *"github.com/${AVAILABLE_REPOSITORY}/"* ]]
}

wget() {
    cp "${FIXTURE}" "${@: -1}"
}

source "${SETUP_PATH}"
install() {
    touch "${INSTALL_FUNCTION_CALLED}"
    return 1
}
_spotify_install_prebuilt_librespot
'''
    env = os.environ.copy()
    result = subprocess.run(
        [
            'bash',
            '-c',
            harness,
            'test-librespot-binary',
            str(tmp_path),
            str(SETUP),
            str(checksums),
            str(fixture),
            str(attempts),
            available_repository,
        ],
        check=False,
        capture_output=True,
        env=env,
        text=True,
    )
    attempted_urls = attempts.read_text().splitlines() if attempts.exists() else []
    return result, attempted_urls


def test_architecture_mapping_and_archive_names():
    harness = r'''
INSTALLATION_PATH="$1"
source "$2"
for machine in armv7l aarch64 x86_64; do
    arch="$(_spotify_librespot_architecture "${machine}")"
    printf '%s=%s=%s\n' \
        "${machine}" "${arch}" "$(_spotify_archive_name "${arch}")"
done
'''
    result = subprocess.run(
        ['bash', '-c', harness, 'test-architecture', str(ROOT), str(SETUP)],
        check=True,
        capture_output=True,
        text=True,
    )

    assert result.stdout.splitlines() == [
        (
            'armv7l=armv7='
            'librespot-303026bb-phoniebox1-linux-armv7.tar.gz'
        ),
        (
            'aarch64=arm64='
            'librespot-303026bb-phoniebox1-linux-arm64.tar.gz'
        ),
        (
            'x86_64=amd64='
            'librespot-303026bb-phoniebox1-linux-amd64.tar.gz'
        ),
    ]


def test_source_repository_is_preferred_and_archive_is_cleaned_up(tmp_path):
    result, attempted_urls = _run_prebuilt_install(tmp_path)

    assert result.returncode == 0, result.stderr
    assert attempted_urls == [
        (
            'https://github.com/contributor/RPi-Jukebox-RFID/releases/'
            'download/librespot-builds/'
            'librespot-303026bb-phoniebox1-linux-amd64.tar.gz'
        ),
    ]
    assert (tmp_path / '.local' / 'bin' / 'librespot').stat().st_mode & 0o111
    assert not (tmp_path / 'install-function-called').exists()
    assert not list((tmp_path / '.cache').glob('librespot-install.*'))


def test_missing_source_archive_falls_back_to_upstream(tmp_path):
    result, attempted_urls = _run_prebuilt_install(
        tmp_path,
        available_repository='MiczFlor',
    )

    assert result.returncode == 0, result.stderr
    assert len(attempted_urls) == 2
    assert 'github.com/contributor/' in attempted_urls[0]
    assert 'github.com/MiczFlor/' in attempted_urls[1]


def test_checksum_rejection_does_not_install_and_cleans_up(tmp_path):
    result, attempted_urls = _run_prebuilt_install(
        tmp_path,
        checksum_matches=False,
    )

    assert result.returncode != 0
    assert len(attempted_urls) == 2
    assert not (tmp_path / '.local' / 'bin' / 'librespot').exists()
    assert not list((tmp_path / '.cache').glob('librespot-install.*'))


def test_missing_archives_do_not_leave_temporary_files(tmp_path):
    result, attempted_urls = _run_prebuilt_install(
        tmp_path,
        available_repository='nobody',
    )

    assert result.returncode != 0
    assert len(attempted_urls) == 2
    assert not (tmp_path / '.local' / 'bin' / 'librespot').exists()
    assert not list((tmp_path / '.cache').glob('librespot-install.*'))


def test_invalid_archive_is_rejected_and_cleaned_up(tmp_path):
    fixture = tmp_path / 'fixture.tar.gz'
    fixture.write_bytes(b'not a tar archive')
    result, _ = _run_prebuilt_install(tmp_path, fixture=fixture)

    assert result.returncode != 0
    assert not (tmp_path / '.local' / 'bin' / 'librespot').exists()
    assert not list((tmp_path / '.cache').glob('librespot-install.*'))


def test_installation_check_uses_directory_verifier_for_cache(tmp_path):
    binary = tmp_path / '.local' / 'bin' / 'librespot'
    binary.parent.mkdir(parents=True)
    binary.write_text('#!/bin/sh\nexit 0\n')
    binary.chmod(0o755)
    (tmp_path / '.cache' / 'librespot').mkdir(parents=True)
    calls = tmp_path / 'verification-calls'
    harness = r'''
HOME_PATH="$1"
SETUP_PATH="$2"
CALLS="$3"
CURRENT_USER=pi
CURRENT_USER_GROUP=pi

print_verify_installation() { :; }
verify_apt_packages() { :; }
verify_files_chown() { printf 'file:%s\n' "$*" >> "${CALLS}"; }
verify_dirs_chown() { printf 'dir:%s\n' "$*" >> "${CALLS}"; }
verify_file_contains_string() { :; }
verify_service_enablement() { :; }
exit_on_error() { exit 42; }

source "${SETUP_PATH}"
_spotify_check
'''
    result = subprocess.run(
        [
            'bash',
            '-c',
            harness,
            'test-librespot-check',
            str(tmp_path),
            str(SETUP),
            str(calls),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    verification_calls = calls.read_text().splitlines()
    assert f'file:pi pi {binary}' in verification_calls
    assert (
        f'dir:pi pi {tmp_path / ".cache" / "librespot"}'
        in verification_calls
    )


def test_committed_checksums_cover_every_supported_architecture():
    entries = {
        line.split()[1]: line.split()[0]
        for line in CHECKSUMS.read_text().splitlines()
        if line and not line.startswith('#')
    }

    assert set(entries) == {
        f'librespot-{BUILD_ID}-linux-amd64.tar.gz',
        f'librespot-{BUILD_ID}-linux-arm64.tar.gz',
        f'librespot-{BUILD_ID}-linux-armv7.tar.gz',
    }
    assert all(len(value) == 64 for value in entries.values())


def test_armv6_option_warns_and_disables_spotify_without_prompting():
    harness = r'''
source "$1"
source "$2"

get_architecture() {
    printf '%s\n' armv6
}
clear_c() {
    :
}
print_c() {
    printf '%s\n' "$1"
}
log() {
    :
}

SETUP_SPOTIFY=true
_option_spotify
printf 'SETUP_SPOTIFY=%s\n' "${SETUP_SPOTIFY}"
'''
    result = subprocess.run(
        [
            'bash',
            '-c',
            harness,
            'test-armv6-option',
            str(DEFAULTS),
            str(OPTIONS),
        ],
        input='y\nunexpected-input\n',
        check=True,
        capture_output=True,
        text=True,
    )

    assert 'Spotify is not yet supported on ARMv6' in result.stdout
    assert 'SETUP_SPOTIFY=false' in result.stdout


def test_preconfigured_armv6_setup_warns_and_continues():
    harness = r'''
INSTALLATION_PATH="$1"
SYSTEMD_USR_PATH=/tmp/systemd
source "$2"

get_architecture() {
    printf '%s\n' armv6
}
print_lc() {
    printf '%s\n' "$1"
}

SETUP_SPOTIFY=true
setup_spotify
printf 'SETUP_SPOTIFY=%s\n' "${SETUP_SPOTIFY}"
'''
    result = subprocess.run(
        ['bash', '-c', harness, 'test-armv6-setup', str(ROOT), str(SETUP)],
        check=True,
        capture_output=True,
        text=True,
    )

    assert 'continuing without Spotify support' in result.stdout
    assert 'SETUP_SPOTIFY=false' in result.stdout


def test_spotify_dependency_selection_uses_only_trixie_runtime_packages():
    harness = r'''
INSTALLATION_PATH="$1"
source "$2"

get_args_from_file() {
    :
}
get_architecture() {
    printf '%s\n' amd64
}

SETUP_MPD=false
SETUP_SPOTIFY=true
ENABLE_SAMBA=false
ENABLE_WEBAPP=false
ENABLE_KIOSK_MODE=false
ENABLE_AUTOHOTSPOT=false
_collect_apt_packages
printf '%s\n' "${APT_PACKAGES[@]}"
'''
    result = subprocess.run(
        [
            'bash',
            '-c',
            harness,
            'test-runtime-dependencies',
            str(ROOT),
            str(PREPARE_DEPENDENCIES),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    packages = result.stdout.splitlines()
    assert packages == ['git', 'ca-certificates', 'libpulse0', 'libssl3t64']
    assert not {'cargo', 'libpulse-dev', 'libssl-dev', 'pkg-config'} & set(
        packages
    )
