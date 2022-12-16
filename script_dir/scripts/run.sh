#!/bin/bash
# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

SCRIPT_PATH=$(realpath "$(dirname -- "${BASH_SOURCE[0]}")")
DIR_PATH=$(dirname "$SCRIPT_PATH")
if [ ! -d $DIR_PATH/venv ]; then
  source $SCRIPT_PATH/create_python_environment.sh
fi
# shellcheck disable=SC1091,SC1090
source "${DIR_PATH}"/venv/bin/activate
sudo env PATH="$PATH" PYTHONPATH="$DIR_PATH" python $DIR_PATH/scr.py
