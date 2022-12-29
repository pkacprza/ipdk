#!/usr/bin/env bash
#
# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#

set -e
set -x
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)

cd "$script_dir"
go build -buildmode=plugin -o ./opi-spdk-bridge-plugin.so ./*.go
cd "$script_dir"/../../../opi-spdk-bridge/server
go build -v -o "$script_dir"/opi-spdk-bridge *.go
cd "$script_dir"

sudo ./opi-spdk-bridge -port=50052 -config=./config.json