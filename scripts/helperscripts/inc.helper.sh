# Reads a textfile and pipes all lines as args to the given command.
# Does filter out comments.
# Arguments:
#   1    : textfile to read
#   2... : command to receive args (e.g. 'echo', 'apt-get -y install', ...)
call_with_args_from_file () {
    local package_file="$1"
    shift

    sed 's|#.*||g' ${package_file} | xargs "$@"
}

# escape relevant chars for strings used in 'sed' commands. implies delimiter char '|'
escape_for_sed() {
	local escaped=$(echo "$1" | sed -e 's/[\&'\''|]/\\&/g')
	echo "$escaped"
}
