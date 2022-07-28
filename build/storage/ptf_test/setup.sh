#!/bin/bash

branch='feat-add-ptf-tests'
git_url='https://github.com/intelfisz/ipdk.git'
ptf_url='https://github.com/p4lang/ptf.git'

mkdir -p "IPDK_workspace"
current_dir=$(pwd)
path_to_clone_ptf="$current_dir/IPDK_workspace/ipdk/build/storage/"

cd "IPDK_workspace" && git clone --branch "$branch" "$git_url"
cd "$path_to_clone_ptf" && git clone "$ptf_url"

cd && mkdir -p "IPDK_workspace/SHARE"