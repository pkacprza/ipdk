#!/usr/bin/env bash
#
# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#


[ "$DEBUG" == 'true' ] && set -x

scripts_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
# shellcheck disable=SC1091
source "$scripts_dir/vm/vm_default_variables.sh"
# shellcheck disable=SC1091
source "$scripts_dir/sma_config_file.sh"

SHARED_VOLUME=${SHARED_VOLUME:-$(realpath .)}
QMP_IP_ADDR="${QMP_IP_ADDR:-${DEFAULT_QMP_ADDRESS}}"
QMP_PORT="${QMP_PORT:-"$DEFAULT_QMP_PORT"}"
SMA_ADDR="${SMA_ADDR:-"0.0.0.0"}"
SMA_PORT="${SMA_PORT:-8080}"
HOT_PLUG_SERVICE_IP_ADDR="${HOT_PLUG_SERVICE_IP_ADDR:-"0.0.0.0"}"
HOT_PLUG_SERVICE_PORT="${HOT_PLUG_SERVICE_PORT:-50051}"


function print_error_and_exit() {
    echo "${1}"
    exit 1
}

function check_all_variables_are_set() {
    number_re='^[0-9]+$'
    ip_addr_re='^(([1-9]?[0-9]|1[0-9][0-9]|2([0-4][0-9]|5[0-5]))\.){3}([1-9]?[0-9]|1[0-9][0-9]|2([0-4][0-9]|5[0-5]))$'

    if [ -z "${SHARED_VOLUME}" ]; then
        print_error_and_exit "SHARED_VOLUME is not defined"
    elif [ ! -d "${SHARED_VOLUME}" ]; then
        print_error_and_exit "SHARED_VOLUME is not a directory"
    elif [ -z "${HOT_PLUG_SERVICE_IP_ADDR}" ]; then
        print_error_and_exit "HOT_PLUG_SERVICE_IP_ADDR is not set"
    elif ! [[ "${HOT_PLUG_SERVICE_IP_ADDR}" =~ ${ip_addr_re} ]]; then
        print_error_and_exit "HOT_PLUG_SERVICE_IP_ADDR does not represent ip address"
    elif [ -z "${HOT_PLUG_SERVICE_PORT}" ]; then
        print_error_and_exit "PORT is not set"
    elif ! [[ "${HOT_PLUG_SERVICE_PORT}" =~ ${number_re} ]] ; then
        print_error_and_exit "PORT is not a number"
    elif ! [[ "${QMP_PORT}" =~ ${number_re} ]] ; then
        print_error_and_exit "QMP_PORT is not a number"
    elif [ -z "${QMP_IP_ADDR}" ]; then
        print_error_and_exit "QMP_IP_ADDR is not set"
    elif ! [[ "${QMP_IP_ADDR}" =~ ${ip_addr_re} ]]; then
        print_error_and_exit "QMP_IP_ADDR does not represent ip address"
    elif [ -z "${SMA_ADDR}" ]; then
        print_error_and_exit "SMA_ADDR is not set"
    elif ! [[ "${SMA_ADDR}" =~ ${ip_addr_re} ]]; then
        print_error_and_exit "SMA_ADDR does not represent ip address"
    elif ! [[ "${SMA_PORT}" =~ ${number_re} ]] ; then
        print_error_and_exit "SMA_PORT is not a number"
    fi
}

check_all_variables_are_set
SHARED_VOLUME=$(realpath "${SHARED_VOLUME}")

tmp_sma_config_file=$(create_sma_config_file "$SHARED_VOLUME" "$QMP_IP_ADDR" \
                        "$QMP_PORT" "$SMA_ADDR" "$SMA_PORT")
function cleanup() {
	rm -f "$tmp_sma_config_file"
}
trap 'cleanup' EXIT

ALLOCATE_HUGEPAGES="true"
BUILD_IMAGE="true"
IMAGE_NAME="proxy-container"
ARGS=()
ARGS+=("-v" "${SHARED_VOLUME}:/${SHARED_VOLUME}")
ARGS+=("-v" "${tmp_sma_config_file}:/sma_config.yml")
ARGS+=("-e" "SPDK_IP_ADDR=${SPDK_IP_ADDR}")
ARGS+=("-e" "SPDK_PORT=${SPDK_PORT}")
ARGS+=("-e" "HOT_PLUG_SERVICE_IP_ADDR=${HOT_PLUG_SERVICE_IP_ADDR}")
ARGS+=("-e" "HOT_PLUG_SERVICE_PORT=${HOT_PLUG_SERVICE_PORT}")
ARGS+=("-e" "HOST_SHARED_VOLUME=${SHARED_VOLUME}")

# shellcheck source=./scripts/run_container.sh
source "${scripts_dir}/run_container.sh"
