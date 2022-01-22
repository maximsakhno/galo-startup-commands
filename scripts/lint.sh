#!/bin/bash

set -x
set -e

mypy galo_startup tests
flake8 galo_startup tests
black galo_startup tests --check
isort galo_startup tests --check-only
bandit galo_startup -r
