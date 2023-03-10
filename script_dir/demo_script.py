# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#

from system_tools.config import TestConfig
from system_tools.config import (HostTargetConfig, IPUStorageConfig,
                                 StorageTargetConfig)
from system_tools.ssh_terminal import SSHTerminal
from dotenv import load_dotenv

load_dotenv()

###Important pre-requisites:
###Docker is installed and running with correct (proxy) settings.
print('Script is starting')
tests_config = TestConfig()
# Linkpartner
#import ipdb; ipdb.set_trace()
linkpartner_terminal = SSHTerminal(StorageTargetConfig())

#ipu_storage_terminal = SSHTerminal(IPUStorageConfig())
# Silicon
silicon_terminal = SSHTerminal(HostTargetConfig())

storage_dir = "ipdk/build/storage"


is_running_container = True


def get_docker_containers_id_from_docker_image_name(terminal, docker_image_name):
    out = terminal.execute(
        f'sudo docker ps | grep "{docker_image_name}"'
    ).splitlines()
    return [line.split()[0] for line in out]

cmd_sender_id = get_docker_containers_id_from_docker_image_name(linkpartner_terminal, "cmd-sender")[0]

def run_cmd_without_error(terminal, cmd):
    try:
        terminal.execute(cmd)
    except:
        print(f"Command '{cmd}' not working")


# all this things shall run in host target so you can run it where you want


# todo install docker



if not is_running_container:
    cmd = 'sudo rmmod nvme'
    run_cmd_without_error(silicon_terminal, cmd)



    # remove old repository
    cmd = "rm -rf ipdk"
    silicon_terminal.execute(cmd)

    # copy repository
    repository_url = "'https://github.com/ipdk-io/ipdk.git'"
    cmd = f"git clone --branch main {repository_url}"
    run_cmd_without_error(silicon_terminal, cmd)


    #import ipdb; ipdb.set_trace()

    # copy customization needet to host target
    CUSTOMIZATION_DIR_IN_CONTAINER = f'{storage_dir}/core/host-target/customizations/device_exerciser_mev.py'
    ftp_client = silicon_terminal.client.open_sftp()
    ftp_client.put('./files/device_exerciser_mev.py', CUSTOMIZATION_DIR_IN_CONTAINER)
    ftp_client.close()

    # rust host_target
    cmd = (
        f"cd {storage_dir} && "
        f"AS_DAEMON=true DEBUG=true IP_ADDR={silicon_terminal.config.ip_address} scripts/run_host_target_container.sh"
    )
    run_cmd_without_error(cmd)


# command sender is in lp so you need docker ip
# and then this command should be send to cmd sender


host_target_ip = ""
ipu_storage_container_ip = "200.1.1.3"
storage_target_ip = "200.1.1.1" # Address visible from IPU side.


def create_sender_cmd(cmd):
    return f"""sudo docker exec {cmd_sender_id} bash -c 'source /scripts/disk_infrastructure.sh; export PYTHONPATH=/; """ \
           f"""{cmd}""" \
           """ '"""




pf_cmd = create_sender_cmd(f"""create_nvme_device {ipu_storage_container_ip} 8080 {host_target_ip} 50051 0 0""")
pf = linkpartner_terminal.execute(pf_cmd)

import ipdb; ipdb.set_trace()
vf1_cmd = create_sender_cmd(f"""create_nvme_device {ipu_storage_container_ip} 8080 {host_target_ip} 50051 0 1""")
vf2_cmd = create_sender_cmd(f"""create_nvme_device {ipu_storage_container_ip} 8080 {host_target_ip} 50051 0 2""")
vf3_cmd = create_sender_cmd(f"""create_nvme_device {ipu_storage_container_ip} 8080 {host_target_ip} 50051 0 3""")
import ipdb; ipdb.set_trace()
vf1 = linkpartner_terminal.execute(vf1_cmd)
vf2 = linkpartner_terminal.execute(vf2_cmd)
vf3 = linkpartner_terminal.execute(vf3_cmd)

import ipdb; ipdb.set_trace()
create_subsystem_cmd = create_sender_cmd(
    f"""create_and_expose_sybsystem_over_tcp {storage_target_ip} nqn.2016-06.io.spdk:cnode0 4420"""
)
import ipdb; ipdb.set_trace()
linkpartner_terminal.execute(create_subsystem_cmd)
import ipdb; ipdb.set_trace()

create_ramdrive_cmd = create_sender_cmd(
    f"""create_ramdrive_and_attach_as_ns_to_subsystem {storage_target_ip} Malloc0 16 nqn.2016-06.io.spdk:cnode0"""
)
import ipdb; ipdb.set_trace()
malloc0 = linkpartner_terminal.execute(create_ramdrive_cmd)

import ipdb; ipdb.set_trace()
attach_cmd = create_sender_cmd(
    f"""attach_crypto_volume_with_aes_xts_cipher "{ipu_storage_container_ip}" "{pf}" "{malloc0}" nqn.2016-06.io.spdk:cnode0  {storage_target_ip} 000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f 100102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f 4420"""
)
import ipdb; ipdb.set_trace()
linkpartner_terminal.execute(attach_cmd)
import ipdb; ipdb.set_trace()

fio_cmd = create_sender_cmd(
    f"""echo -e $(no_grpc_proxy="" grpc_cli call {host_target_ip}:50051 RunFio "diskToExercise: {{ deviceHandle: '$pf' volumeId: '$malloc0'}} fioArgs: '{{\"rw\":\"randrw\",\"runtime\":5, \"numjobs\": 1, \"time_based\": 1, \"group_reporting\": 1 }}'")"""
)
import ipdb; ipdb.set_trace()
fio = linkpartner_terminal.execute(fio_cmd)
import ipdb; ipdb.set_trace()

print(fio)
print('script finished')

