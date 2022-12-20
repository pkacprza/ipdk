# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#

from system_tools.config import TestConfig
from system_tools.config import (HostTargetConfig, IPUStorageConfig,
                                 StorageTargetConfig)
from system_tools.ssh_terminal import SSHTerminal


###Important pre-requisites:
###Docker is installed and running with correct (proxy) settings.
print('Script is starting')
tests_config = TestConfig()
# Linkpartner
storage_target_terminal = SSHTerminal(StorageTargetConfig())

ipu_storage_terminal = SSHTerminal(IPUStorageConfig())
# Silicon
host_target_terminal = SSHTerminal(HostTargetConfig())

storage_dir = "ipdk/build/storage"
cmd = 'sudo rmmod nvme'
try:
    host_target_terminal.execute(cmd)
except:
    print("sudo rmod nvme didn't work")
    pass

# copy repository
repository_url = "'https://github.com/ipdk-io/ipdk.git'"
cmd = f"git clone --branch main {repository_url}"

try:
    host_target_terminal.execute(cmd)
except:
    print("host target didn't download repo")
    pass

try:
    storage_target_terminal.execute(cmd)
except:
    print("storage target target didn't download repo")
    pass


# todo copy file


# rust host_target
cmd = (
    f"cd {storage_dir} && "
    f"AS_DAEMON=true scripts/run_host_target_container.sh"
)
try:
    host_target_terminal.execute(cmd)
except:
    print("host target didn't run")
    pass

cmd = 'cd ipdk/build/storage/scripts && sudo DEBUG=true ./run_cmd_sender.sh'
storage_target_terminal.execute(cmd)

cmd_export = f'export host_target_ip="10.55.218.158" ;' \
    f' export ipu_storage_container_ip="200.1.1.5" ;' \
    f' export storage_target_ip="200.1.1.1" # Address visible from IPU side.'

storage_target_terminal.execute(cmd_export)

cmd_pf_creation = f'pf=$(create_nvme_device $ipu_storage_container_ip 8080 $host_target_ip 50051 0 0)'

storage_target_terminal.execute(cmd_pf_creation)

cmd_ramdrive_creation = f'create_and_expose_sybsystem_over_tcp' \
    f'$storage_target_ip nqn.2016-06.io.spdk:cnode0 4420 ;' \
    f'malloc0=$(create_ramdrive_and_attach_as_ns_to_subsystem' \
    f'$storage_target_ip Malloc0 16 nqn.2016-06.io.spdk:cnode0) ; echo $malloc0'

storage_target_terminal.execute(cmd_ramdrive_creation)

cmd_volume_attach = f'attach_volume $ipu_storage_container_ip "$pf" "$malloc0" nqn.2016-06.io.spdk:cnode0 $storage_target_ip 4420'

cmd_fio = f"""echo -e $(no_grpc_proxy="" grpc_cli call $host_target_ip:50051""" \
    f""" RunFio "diskToExercise: {{ deviceHandle: '$pf' volumeId: '$malloc0'}}""" \
    f""" fioArgs: '{{\"rw\":\"randrw\",\"runtime\":5, \"numjobs\": 1,""" \
    f"""'\"time_based\": 1, \"group_reporting\": 1 }}'")'"""

fio = storage_target_terminal.execute(cmd_fio)
print(fio)
print('script finished')
