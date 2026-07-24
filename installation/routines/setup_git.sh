GIT_ABORT_MSG="Aborting dir to git repo conversion.
Your directory content is untouched, you simply cannot use git for updating / developing"

_git_fetch_origin() {
  if [[ "$GIT_USE_SSH" == true ]]; then
    # Avoid an interactive host-key prompt during installation.
    git -c core.sshCommand='ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no' fetch "$@"
  else
    git fetch "$@"
  fi
}

_git_add_upstream_remote() {
  if [[ "$GIT_USER" == "$GIT_UPSTREAM_USER" ]]; then
    return
  fi

  if [[ "$GIT_USE_SSH" == true ]]; then
    git remote add upstream "git@github.com:${GIT_UPSTREAM_USER}/${GIT_REPO_NAME}.git"
  else
    git remote add upstream "https://github.com/${GIT_UPSTREAM_USER}/${GIT_REPO_NAME}.git"
  fi
}

_git_fetch_requested_branch() {
  local branch_refspec="refs/heads/${GIT_BRANCH}:refs/remotes/origin/${GIT_BRANCH}"

  if ! _git_fetch_origin --depth=1 --no-tags origin "$branch_refspec"; then
    return 1
  fi

  if ! git cat-file -e "${GIT_HASH}^{commit}" 2>/dev/null; then
    log "*** Downloaded commit is not the current branch tip; deepening by 50 commits"
    _git_fetch_origin --deepen=50 --no-tags origin "$branch_refspec" || return 1
  fi

  if ! git cat-file -e "${GIT_HASH}^{commit}" 2>/dev/null; then
    log "*** Downloaded commit is still unresolved; fetching full branch history"
    _git_fetch_origin --unshallow --no-tags origin "$branch_refspec" || return 1
  fi

  if ! git cat-file -e "${GIT_HASH}^{commit}" 2>/dev/null; then
    log "Error: downloaded commit ${GIT_HASH} is not in ${GIT_BRANCH}"
    return 1
  fi
}

_git_convert_tardir_git_repo() {
  log "****************************************************
*** Converting tar-ball download into git repository
****************************************************"

  git -c init.defaultBranch=main init
  git config pull.rebase false

  if [[ $GIT_USE_SSH == true ]]; then
    git remote add origin "git@github.com:${GIT_USER}/${GIT_REPO_NAME}.git"
    log "\n*** Git fetch (SSH) *******************************"
    if ! _git_fetch_requested_branch; then
      log "\n*** NOTICE *****************************************
* Error in getting Git Repository using SSH! USING FALLBACK HTTPS.
* Note: This is only relevant for developers!
* Did you forget to upload the ssh key for this machine to GitHub?
* Defaulting to HTTPS protocol. You can change back to SSH later with
* git remote set-url origin git@github.com:${GIT_USER}/${GIT_REPO_NAME}.git
* git remote set-url upstream git@github.com:${GIT_UPSTREAM_USER}/${GIT_REPO_NAME}.git\n"

      git remote remove origin
      GIT_USE_SSH=false
    fi
  fi

  if [[ $GIT_USE_SSH == false ]]; then
    git remote add origin "https://github.com/${GIT_USER}/${GIT_REPO_NAME}.git"
    log "\n*** Git fetch (HTTPS) *****************************"
    if ! _git_fetch_requested_branch; then
      log "Error: Could not fetch repository!"
      log "$GIT_ABORT_MSG"
      return 1
    fi
  fi

  _git_add_upstream_remote

  HASH_BRANCH=$(git rev-parse "refs/remotes/origin/${GIT_BRANCH}") || { echo -e "$GIT_ABORT_MSG"; return 1; }
  log "\n*** FETCH_HEAD ($GIT_BRANCH) = $HASH_BRANCH"

  git add .
  GIT_HASH=$(git rev-parse "${GIT_HASH}^{commit}") || { echo -e "$GIT_ABORT_MSG"; return 1; }
  log "*** Git checkout commit"
  git -c advice.detachedHead=false checkout "$GIT_HASH" || { echo -e "$GIT_ABORT_MSG"; return 1; }
  HASH_HEAD=$(git rev-parse HEAD) || { echo -e "$GIT_ABORT_MSG"; return 1; }
  log "*** REQUESTED COMMIT = $HASH_HEAD"

  log "*** Git initialize branch"
  git checkout -b "$GIT_BRANCH"
  git branch --set-upstream-to="origin/$GIT_BRANCH" "$GIT_BRANCH"

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
  git log --oneline --decorate -n 5 HEAD "origin/$GIT_BRANCH"
  log "*** Git describe ***********************************"
  git describe --always --dirty
  log "****************************************************"

  cp -f .githooks/* .git/hooks

  unset HASH_HEAD
  unset HASH_BRANCH
}

_git_repo_check() {
    print_verify_installation

    verify_apt_packages git
    verify_dirs_chown "${CURRENT_USER}" "${CURRENT_USER_GROUP}" "${INSTALLATION_PATH}/.git"
}

_run_init_git_repo_from_tardir() {
    cd "${INSTALLATION_PATH}" || exit_on_error
    _git_convert_tardir_git_repo || exit_on_error "$GIT_ABORT_MSG"
    _git_repo_check
}

init_git_repo_from_tardir() {
    run_with_log_frame _run_init_git_repo_from_tardir "Install Git & init repository"
}
