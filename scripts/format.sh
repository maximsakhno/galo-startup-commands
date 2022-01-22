#!/bin/bash

set -x

autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place galo_startup tests
black galo_startup tests
isort galo_startup tests
