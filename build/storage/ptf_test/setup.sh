#!/bin/bash

branch='feat-add-ptf-tests'
git_url='https://github.com/intelfisz/ipdk.git'
ptf_url='https://github.com/p4lang/ptf.git'

current_dir=$(pwd)
storage_path="$current_dir/IPDK_workspace/ipdk/build/storage/"
spdk_path="$storage_path/spdk"

mkdir -p "IPDK_workspace"
cd "IPDK_workspace" && git clone --branch "$branch" "$git_url"
cd "$storage_path" && git clone "$ptf_url"
cd "$storage_path" && git submodule update --init --recursive --force
cd "$spdk_path"
sudo scripts/pkgdep.sh
sudo dnf install -y kernel-headers
sudo ./configure --with-sma --without-isal
sudo make
cd && mkdir -p "IPDK_workspace/SHARE"
