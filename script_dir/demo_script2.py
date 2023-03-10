# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#

from system_tools.config import HostTargetConfig, StorageTargetConfig
from system_tools.ssh_terminal import SSHTerminal
from dotenv import load_dotenv

load_dotenv()


ipu_storage_container_ip = "200.1.1.3"
storage_target_ip = "200.1.1.2"  # Address visible from IPU side.

print('Script is starting')
# Linkpartner
linkpartner_terminal = SSHTerminal(StorageTargetConfig())

host_target_ip = HostTargetConfig().ip_address

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

# command sender is in lp so you need docker ip
# and then this command should be send to cmd sender


def create_sender_cmd(cmd):
    return f"""sudo docker exec {cmd_sender_id} bash -c 'source /scripts/disk_infrastructure.sh; export PYTHONPATH=/; """ \
           f"""{cmd}""" \
           """ '"""


# start operation on cmd_sender
pf_cmd = create_sender_cmd(f"""create_nvme_device {ipu_storage_container_ip} 8080 {host_target_ip} 50051 0 0""")
pf = linkpartner_terminal.execute(pf_cmd)

create_subsystem_cmd = create_sender_cmd(
    f"""create_and_expose_sybsystem_over_tcp {storage_target_ip} nqn.2016-06.io.spdk:cnode0 4420"""
)
linkpartner_terminal.execute(create_subsystem_cmd)

create_ramdrive_cmd = create_sender_cmd(
    f"""create_ramdrive_and_attach_as_ns_to_subsystem {storage_target_ip} Malloc0 16 nqn.2016-06.io.spdk:cnode0"""
)
malloc0 = linkpartner_terminal.execute(create_ramdrive_cmd)

# todo check
attach_cmd = create_sender_cmd(
    f"""attach_volume {ipu_storage_container_ip} "{pf}" "{malloc0}" nqn.2016-06.io.spdk:cnode0 {storage_target_ip} 4420"""
)
linkpartner_terminal.execute(attach_cmd)

import ipdb; ipdb.set_trace()
create_ramdrive_cmd = create_sender_cmd(
    f"""create_ramdrive_and_attach_as_ns_to_subsystem {storage_target_ip} Malloc1 16 nqn.2016-06.io.spdk:cnode0"""
)
malloc1 = linkpartner_terminal.execute(create_ramdrive_cmd)
attach_cmd = create_sender_cmd(
    f"""attach_volume {ipu_storage_container_ip} "{pf}" "{malloc1}" nqn.2016-06.io.spdk:cnode0 {storage_target_ip} 4420"""
)
linkpartner_terminal.execute(attach_cmd)



import ipdb; ipdb.set_trace()


cmd = f"""grpc_cli call {host_target_ip}:50051 RunFio""" \
      f""" "diskToExercise: {{ deviceHandle: '{pf}' volumeId: '{malloc0}' }} fioArgs: """ \
      f"""'{{\\"rw\\":\\"randrw\\", \\"runtime\\":1, \\"numjobs\\": 1, \\"time_based\\": 1, """ \
      f"""\\"group_reporting\\": 1 }}'" """
fio_cmd = create_sender_cmd(
    cmd
)
fio1 = linkpartner_terminal.execute(fio_cmd)
cmd = f"""grpc_cli call {host_target_ip}:50051 RunFio""" \
      f""" "diskToExercise: {{ deviceHandle: '{pf}' volumeId: '{malloc1}' }} fioArgs: """ \
      f"""'{{\\"rw\\":\\"randrw\\", \\"runtime\\":1, \\"numjobs\\": 1, \\"time_based\\": 1, """ \
      f"""\\"group_reporting\\": 1 }}'" """
fio_cmd = create_sender_cmd(
    cmd
)
fio2 = linkpartner_terminal.execute(fio_cmd)

import ipdb; ipdb.set_trace()
delete_cmd = create_sender_cmd(
    f"""delete_nvme_device {ipu_storage_container_ip} 8080 {host_target_ip} 50051 {pf}"""
)

print(fio)
print('script finished')

