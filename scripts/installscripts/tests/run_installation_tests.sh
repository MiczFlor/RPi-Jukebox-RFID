#!/usr/bin/env bash

# Install Phoniebox and test it
# Used e.g. for tests on Docker

# TODO path code for Docker to be removed

# print current path
echo $PWD

# run installation
./code/scripts/installscripts/buster-install-default.sh

# test installation
./code/scripts/installscripts/tests/test_installation.sh
