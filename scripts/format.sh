#!/bin/bash

set -x

autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place galo_startup_commands tests
black galo_startup_commands tests
isort galo_startup_commands tests
