# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#

from system_tools.config import TestConfig
from system_tools.config import (HostTargetConfig, IPUStorageConfig,
                                 StorageTargetConfig)
from system_tools.ssh_terminal import SSHTerminal


print('poczatek skryptu')
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
    pass

# copy repository
repository_url = "'https://github.com/ipdk-io/ipdk.git'"
cmd = f"git clone --branch main {repository_url}"
try:
    host_target_terminal.execute(cmd)
except:
    pass
try:
    storage_target_terminal.execute(cmd)
except:
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
    pass

cmd = 'cd ipdk/build/storage/scripts && sudo DEBUG=true ./run_cmd_sender.sh'
storage_target_terminal.execute(cmd)



print('koniec skryptu')