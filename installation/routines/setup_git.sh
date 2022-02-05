GIT_ABORT_MSG="Aborting dir to git repo conversion.
Your directory content is untouched, you simply cannot use git for updating / developing"

_git_install_os_dependencies() {
  echo "Install Git dependencies"
  sudo apt-get -y update; sudo apt-get -y install \
    git \
    --no-install-recommends \
    --allow-downgrades \
    --allow-remove-essential \
    --allow-change-held-packages
}

_git_convert_tardir_git_repo() {
  echo "****************************************************"
  echo "*** Converting tar-ball download into git repository"
  echo "****************************************************"

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
    echo "*** Git fetch (SSH) *******************************"
    # Prevent: The authenticity of host 'github.com (140.82.121.4)' can't be established.
    # Do only for this one command, so we do not disable the checks forever
    if ! git -c core.sshCommand='ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no' fetch origin "${GIT_BRANCH}" --set-upstream --shallow-since=2021-04-21 --tags;
    then
      echo ""
      echo "*** NOTICE *****************************************"
      echo "* Error in getting Git Repository using SSH! USING FALLBACK HTTPS."
      echo "* Note: This is only relevant for developers!"
      echo "* Did you forget to upload the ssh key for this machine to GitHub?"
      echo "* Defaulting to HTTPS protocol. You can change back to SSH later with"
      echo "* git remote set-url origin git@github.com:${GIT_USER}/${GIT_REPO_NAME}.git"
      echo "* git remote set-url upstream git@github.com:${GIT_UPSTREAM_USER}/${GIT_REPO_NAME}.git"
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
      echo "*** Git fetch (HTTPS) *****************************"
    if ! git fetch origin --set-upstream --shallow-since=2021-04-21 --tags "${GIT_BRANCH}"; then
      echo "Error: Could not fetch repository!"
      echo -e "$GIT_ABORT_MSG"
      return
    fi
  fi
  HASH_BRANCH=$(git rev-parse FETCH_HEAD) || { echo -e "$GIT_ABORT_MSG"; return; }
  echo "*** FETCH_HEAD ($GIT_BRANCH) = $HASH_BRANCH"

  git add .
  # Checkout the exact hash that we have downloaded as tarball
  echo "*** Git checkout commit"
  git -c advice.detachedHead=false checkout "$GIT_HASH" || { echo -e "$GIT_ABORT_MSG"; return; }
  HASH_HEAD=$(git rev-parse HEAD) || { echo -e "$GIT_ABORT_MSG"; return; }
  echo "*** REQUESTED COMMIT = $HASH_HEAD"

  # Let's move onto the relevant branch, WITHOUT touching the current checked-out commit
  # Since we have fetched with --set-upstream above this initializes the tracking branch
  echo "*** Git initialize branch"
  git checkout -b "$GIT_BRANCH"

  if [[ "$GIT_USER" != "$GIT_UPSTREAM_USER" ]]; then
    echo "*** Get upstream release tags"
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
      echo "*** Preparing ${GIT_BRANCH_RELEASE} in background"
      echo -e "$OUTPUT"
    fi
    unset OUTPUT
  fi
  if [[ $GIT_BRANCH != "${GIT_BRANCH_DEVELOP}" ]]; then
    OUTPUT=$(git fetch origin --shallow-since=2021-04-21 --tags "${GIT_BRANCH_DEVELOP}" 2>&1)
    if [[ $? -ne 128 ]]; then
      echo "*** Preparing ${GIT_BRANCH_DEVELOP} in background"
      echo -e "$OUTPUT"
    fi
    unset OUTPUT
  fi

  # Provide some status outputs to the user
  if [[ "${HASH_BRANCH}" != "${HASH_HEAD}" ]]; then
    echo "*** IMPORTANT NOTICE *******************************"
    echo "* Your requested branch has moved on while you were installing."
    echo "* Don't worry! We will stay within the the exact download version!"
    echo "* But we set up the git repo to be ready for updating."
    echo "* To start updating (observe updating guidelines!), do:"
    echo "* $ git pull origin $GIT_BRANCH"
  fi

  echo "*** Git remotes ************************************"
  git remote -v
  echo "*** Git status *************************************"
  git status -sb
  echo "*** Git log ****************************************"
  git log --oneline "HEAD^..origin/$GIT_BRANCH"
  echo "*** Git describe ***********************************"
  git describe --tag --dirty='-dirty'
  echo "****************************************************"

  cp -f .githooks/* .git/hooks

  unset HASH_HEAD
  unset HASH_BRANCH
}

init_git_repo_from_tardir() {
  echo "Install Git & init repository" | tee /dev/fd/3

  cd "${INSTALLATION_PATH}" || exit_on_error
  _git_install_os_dependencies
  _git_convert_tardir_git_repo

  echo "DONE: init_git_repo_from_tardir"
}
