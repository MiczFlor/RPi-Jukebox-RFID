#!/usr/bin/env bash

# Install Phoniebox and test it
# Used e.g. for tests on Docker

# print current path
echo $PWD

# run installation
./scripts/installscripts/buster-install-default.sh

# test installation
./scripts/installscripts/tests/test_installation.sh
