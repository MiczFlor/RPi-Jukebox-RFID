GIT_ABORT_MSG="Aborting dir to git repo conversion.
Your directory content is untouched, you simply cannot use git for updating / developing"

_git_install_os_dependencies() {
  log "  Install Git dependencies"
  sudo apt-get -y update; sudo apt-get -y install \
    git \
    --no-install-recommends \
    --allow-downgrades \
    --allow-remove-essential \
    --allow-change-held-packages
}

_git_convert_tardir_git_repo() {
  log "****************************************************
*** Converting tar-ball download into git repository
****************************************************"

  # Just in case, the git version is not new enough, we split up git init -b "${GIT_BRANCH}" into:
  git -c init.defaultBranch=main init
  git checkout -q -b "${GIT_BRANCH}"
  git config pull.rebase false

  # We always add origin as the selected (possible) user repository
  # and, if relevant, MiczFlor's repository as upstream
  # This means for developers everything is fully set up.
  # For users there is no difference there is only origin = MiczFlor
  # We need to get the branch with larger depth, as we do not know
  # how many commits happened between download and git repo init
  # We simply get everything from the beginning of future 3 development but excluding Version 2.X
  if [[ $GIT_USE_SSH == true ]]; then
    git remote add origin "git@github.com:${GIT_USER}/${GIT_REPO_NAME}.git"
    log "\n*** Git fetch (SSH) *******************************"
    # Prevent: The authenticity of host 'github.com (140.82.121.4)' can't be established.
    # Do only for this one command, so we do not disable the checks forever
    if ! git -c core.sshCommand='ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no' fetch origin "${GIT_BRANCH}" --set-upstream --shallow-since=2021-04-21 --tags;
    then
      log "\n*** NOTICE *****************************************
* Error in getting Git Repository using SSH! USING FALLBACK HTTPS.
* Note: This is only relevant for developers!
* Did you forget to upload the ssh key for this machine to GitHub?
* Defaulting to HTTPS protocol. You can change back to SSH later with
* git remote set-url origin git@github.com:${GIT_USER}/${GIT_REPO_NAME}.git
* git remote set-url upstream git@github.com:${GIT_UPSTREAM_USER}/${GIT_REPO_NAME}.git\n"

      git remote remove origin
      GIT_USE_SSH=false
    else
      # Only add upstream with SSH when fetch over SSH succeeded
      if [[ "$GIT_USER" != "$GIT_UPSTREAM_USER" ]]; then
        git remote add upstream "git@github.com:${GIT_UPSTREAM_USER}/${GIT_REPO_NAME}.git"
      fi
    fi
  fi

  if [[ $GIT_USE_SSH == false ]]; then
    git remote add origin "https://github.com/${GIT_USER}/${GIT_REPO_NAME}.git"
    if [[ "$GIT_USER" != "$GIT_UPSTREAM_USER" ]]; then
      git remote add upstream "https://github.com/${GIT_UPSTREAM_USER}/${GIT_REPO_NAME}.git"
    fi
    log "\n*** Git fetch (HTTPS) *****************************"
    if ! git fetch origin --set-upstream --shallow-since=2021-04-21 --tags "${GIT_BRANCH}"; then
      log "Error: Could not fetch repository!"
      log "$GIT_ABORT_MSG"
      return
    fi
  fi
  HASH_BRANCH=$(git rev-parse FETCH_HEAD) || { echo -e "$GIT_ABORT_MSG"; return; }

  log "\n*** FETCH_HEAD ($GIT_BRANCH) = $HASH_BRANCH"

  git add .
  # Checkout the exact hash that we have downloaded as tarball
  log "*** Git checkout commit"
  git -c advice.detachedHead=false checkout "$GIT_HASH" || { echo -e "$GIT_ABORT_MSG"; return; }
  HASH_HEAD=$(git rev-parse HEAD) || { echo -e "$GIT_ABORT_MSG"; return; }
  log "*** REQUESTED COMMIT = $HASH_HEAD"

  # Let's move onto the relevant branch, WITHOUT touching the current checked-out commit
  # Since we have fetched with --set-upstream above this initializes the tracking branch
  log "*** Git initialize branch"
  git checkout -b "$GIT_BRANCH"

  if [[ "$GIT_USER" != "$GIT_UPSTREAM_USER" ]]; then
    log "*** Get upstream release tags"
    # Always get the upstream release branch to get all release tags
    # in case they have not been copied to user repository
    git fetch upstream --shallow-since=2021-04-21 --tags "${GIT_BRANCH_RELEASE}"
  fi

  # Done! Directory is all set up as git repository now!

  # In case we get a non-develop or non-main branch, we speculatively
  # try to get these branches, so they can be checkout out with
  # git checkout ${GIT_BRANCH_DEVELOP}
  # without the need to set up the remote tracking information
  # However, in a user repository, these may not be present, so we suppress output in these cases
  if [[ $GIT_BRANCH != "${GIT_BRANCH_RELEASE}" ]]; then
    OUTPUT=$(git fetch origin --shallow-since=2021-04-21 --tags "${GIT_BRANCH_RELEASE}" 2>&1)
    if [[ $? -ne 128 ]]; then
      log "*** Preparing ${GIT_BRANCH_RELEASE} in background"
      echo -e "$OUTPUT"
    fi
    unset OUTPUT
  fi
  if [[ $GIT_BRANCH != "${GIT_BRANCH_DEVELOP}" ]]; then
    OUTPUT=$(git fetch origin --shallow-since=2021-04-21 --tags "${GIT_BRANCH_DEVELOP}" 2>&1)
    if [[ $? -ne 128 ]]; then
      log "*** Preparing ${GIT_BRANCH_DEVELOP} in background"
      echo -e "$OUTPUT"
    fi
    unset OUTPUT
  fi

  # Provide some status outputs to the user
  if [[ "${HASH_BRANCH}" != "${HASH_HEAD}" ]]; then
    log "\n*** IMPORTANT NOTICE *******************************
* Your requested branch has moved on while you were installing.
* Don't worry! We will stay within the exact download version!
* But we set up the git repo to be ready for updating.
* To start updating (observe updating guidelines!), do:
* $ git pull origin $GIT_BRANCH\n"

  fi

  log "*** Git remotes ************************************"
  git remote -v
  log "*** Git status *************************************"
  git status -sb
  log "*** Git log ****************************************"
  git log --oneline "HEAD^..origin/$GIT_BRANCH"
  log "*** Git describe ***********************************"
  git describe --tag --dirty='-dirty'
  log "****************************************************"

  cp -f .githooks/* .git/hooks

  unset HASH_HEAD
  unset HASH_BRANCH
}

_git_repo_check() {
    print_verify_installation

    verify_apt_packages git
    verify_dirs_chmod_chown 755 "${CURRENT_USER}" "${CURRENT_USER_GROUP}" "${INSTALLATION_PATH}/.git"
}

_run_init_git_repo_from_tardir() {
    cd "${INSTALLATION_PATH}" || exit_on_error
    _git_install_os_dependencies
    _git_convert_tardir_git_repo
    _git_repo_check
}

init_git_repo_from_tardir() {
    run_with_log_frame _run_init_git_repo_from_tardir "Install Git & init repository"
}
