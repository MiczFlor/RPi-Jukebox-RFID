convert_tardir_git_repo() {
  echo "****************************************************"
  echo "*** Converting tar-ball download into git repository"
  echo "****************************************************"

  git init -b "${GIT_BRANCH}"
  git config pull.rebase false

  # We always add origin as the selected (possible) user repository
  # and MiczFlor's repository as upstream
  # This means for developers everything is fully set up.
  # For users there is no difference (origin = upstream = MiczFlor)
  # We need to get the branch with larger depth, as we do not know
  # how many commits happened between download and git repo init
  if [[ $GIT_USE_SSH = true ]]; then
      git remote add origin "git@github.com:${GIT_USER}/${GIT_REPO_NAME}.git"
      git remote add upstream "git@github.com:MiczFlor/${GIT_REPO_NAME}.git"
    if [[ $(git fetch origin "${GIT_BRANCH}") -ne 0 ]]; then
      echo "*** Git fetch *************************************"
      echo "Error in getting Git Repository using SSH!"
      echo "Did you forget to upload the ssh key for this machine to GitHub?"
      echo "Defaulting to HTTPS protocol. You can change back to SSH later with"
      echo "git remote set-url origin git@github.com:${GIT_USER}/${GIT_REPO_NAME}.git"
      echo "git remote set-url upstream git@github.com:MiczFlor/${GIT_REPO_NAME}.git"
      echo "*** Git remotes ***********************************"
      GIT_USE_SSH=false
    fi
  fi

  if [[ $GIT_USE_SSH = false ]]; then
      git remote add origin "https://github.com/${GIT_USER}/${GIT_REPO_NAME}.git"
      git remote add upstream "https://github.com/MiczFlor/${GIT_REPO_NAME}.git"
      git fetch origin "${GIT_BRANCH}"
  fi

  # In case we get a non-develop or non-main branch, we speculatively
  # try to get these branches, so they can be checkout out with
  # git checkout future3/develop
  # without the need to set up the remote tracking information
  # However, in a user repository, these may not be present, so we suppress output in these cases
  if [[ $GIT_BRANCH != "future3/main" ]]; then
    OUTPUT=$(git fetch origin "future3/main" --depth 1 2>&1)
    if [[ $? -ne 128 ]]; then
      echo -e "$OUTPUT"
    fi
  fi
  if [[ $GIT_BRANCH != "future3/develop" ]]; then
    OUTPUT=$(git fetch origin "future3/develop" --depth 1 2>&1)
    if [[ $? -ne 128 ]]; then
      echo -e "$OUTPUT"
    fi
  fi

  git add .
  # Checkout the exact Hash that we have downloaded as tarball
  git -c advice.detachedHead=false checkout "$GIT_HASH"
  # We also pull the branch the Hash belongs to
  git pull origin "$GIT_BRANCH" 2>&1
  if  [[ $? -ne 0 ]]; then
    echo "*** Git pull ***************************************"
    echo "FAILED to pull repository into existing directory"
    echo "Your Box will run ok, but you need to fix the"
    echo "git state before doing any git pulls or updating"
    echo "****************************************************"
  else
    # Not necessary
    # git branch "--set-upstream-to=origin/${GIT_BRANCH}" "$GIT_BRANCH"
    # This initializes the tracking branch
    git checkout "$GIT_BRANCH"
    # But lets go back to our special hash
    git -c advice.detachedHead=false checkout "$GIT_HASH"
    echo "*** Git remotes ************************************"
    git remote -v
    echo "*** Git status *************************************"
    git status -sb
    echo "*** Git log ****************************************"
    git log --oneline "HEAD^..origin/$GIT_BRANCH"
    echo "****************************************************"
    echo "You are now in detachedHead state to match"
    echo "the exact download version. To start updating, do"
    echo "$ git checkout $GIT_BRANCH"
    echo "****************************************************"
  fi
  cp -f .githooks/* .git/hooks

}

update_git_repo() {
  echo "Update Git repository: Branch='${GIT_BRANCH}'"
  cd ${INSTALLATION_PATH}
  TIMESTAMP=$(date +%s)

  # Git Repo has local changes
  if [[ $(git status --porcelain) ]]; then
    echo "  Found local changes in git repository.
  Moving them to backup branch 'local-backup-${TIMESTAMP}' and git stash"
    git fetch origin --depth 1
    git checkout -b local-backup-${TIMESTAMP}
    git stash
    git checkout ${GIT_BRANCH}
    git reset --hard origin/${GIT_BRANCH}
  else
    echo "  Updating version"
    git pull origin $(git rev-parse --abbrev-ref HEAD)
  fi
}
