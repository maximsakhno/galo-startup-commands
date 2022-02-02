#!/bin/bash

set -x
set -e

mypy galo_startup_commands tests
flake8 galo_startup_commands tests
black galo_startup_commands tests --check
isort galo_startup_commands tests --check-only
bandit galo_startup_commands -r
