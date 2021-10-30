#!/usr/bin/env bash

init_git_repo() {
  echo "Init Git repo and add remote url '${GIT_URL}.git' with branch '${GIT_BRANCH}'"
  cd ${INSTALLATION_PATH}
  git init
  git remote add origin ${GIT_URL}.git
  git fetch origin --depth 1
  git add .
  git checkout ${GIT_BRANCH}
  git reset --hard
  echo "DONE: setup_jukebox_core"
}

update_git_repo() {
  echo "Update Git repository: Branch='${GIT_BRANCH}'"
  cd ${INSTALLATION_PATH}
  TIMESTAMP=$(date +%s)

  # Git Repo has local changes
  if [[ `git status --porcelain` ]]; then
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
