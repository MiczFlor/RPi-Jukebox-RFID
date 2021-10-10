#!/usr/bin/env bash

# PIs with little memory need this to finish building the Webapp
export NODE_OPTIONS=--max-old-space-size=512

# In rare cases you will need to update the npm dependencies
# This is the case when the package.json changed
UPDATE_PACK=$(git diff HEAD~1 package.json | wc -l)
if [[ $UPDATE_PACK -gt 0 ]]
then
  npm install
fi

# Rebuild Web App
npm run build