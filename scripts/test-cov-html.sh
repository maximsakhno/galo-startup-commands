#!/bin/bash

set -x

pytest --cov galo_startup_commands --cov-report html tests
