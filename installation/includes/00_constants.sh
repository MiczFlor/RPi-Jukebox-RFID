RPI_BOOT_CONFIG_FILE="/boot/config.txt"
SHARED_PATH="${INSTALLATION_PATH}/shared"
SETTINGS_PATH="${SHARED_PATH}/settings"
SYSTEMD_USR_PATH="/usr/lib/systemd/user/"

# The default upstream user, release branch, and develop branch
# These are used to prepare the repo for developers
# but are not relevant for "production" checkouts
GIT_UPSTREAM_USER=${GIT_UPSTREAM_USER:-MiczFlor}
GIT_BRANCH_RELEASE=${GIT_BRANCH_RELEASE:-future3/main}
GIT_BRANCH_DEVELOP=${GIT_BRANCH_DEVELOP:-future3/develop}

# This message will be displayed at the end of the installation process
# Functions wanting to have something important printed at the end should APPEND to this variable
FIN_MESSAGE=""
