SHARED_PATH="${INSTALLATION_PATH}/shared"
SETTINGS_PATH="${SHARED_PATH}/settings"
SYSTEMD_PATH="/etc/systemd/system"
SYSTEMD_USR_PATH="/usr/lib/systemd/user"
VIRTUAL_ENV="${INSTALLATION_PATH}/.venv"
# Do not change this directory! It must match MPDs expectation where to find the user configuration
MPD_CONF_PATH="${HOME}/.config/mpd/mpd.conf"

# The default upstream user, release branch, and develop branch
# These are used to prepare the repo for developers
# but are not relevant for "production" checkouts
GIT_UPSTREAM_USER=${GIT_UPSTREAM_USER:-MiczFlor}
GIT_BRANCH_RELEASE=${GIT_BRANCH_RELEASE:-future3/main}
GIT_BRANCH_DEVELOP=${GIT_BRANCH_DEVELOP:-future3/develop}

# This message will be displayed at the end of the installation process
# Functions wanting to have something important printed at the end should APPEND to this variable
# example:
# local tmp_fin_message="A Message"
# FIN_MESSAGE="${FIN_MESSAGE:+$FIN_MESSAGE\n}${tmp_fin_message}"
FIN_MESSAGE=""
