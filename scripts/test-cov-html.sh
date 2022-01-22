#!/bin/bash

set -x

pytest --cov galo_startup --cov-report html tests
