# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#

from typing import Optional

from paramiko.client import AutoAddPolicy, SSHClient

from system_tools.config import (HostTargetConfig, IPUStorageConfig,
                                 StorageTargetConfig)
from system_tools.test_platform import (Docker, HostTargetPlatform,
                                        IPUStoragePlatform,
                                        StorageTargetPlatform)


class CommandException(Exception):
    """Custom Exception raises if error occurs during command execution"""


class SSHTerminal:
    """A class used to represent a session with an SSH server"""

    def __init__(self, config, *args, **kwargs):
        self.config = config
        self.client = SSHClient()

        self.client.load_system_host_keys()
        self.client.set_missing_host_key_policy(AutoAddPolicy)
        self.client.connect(
            config.ip_address,
            config.port,
            config.username,
            config.password,
            *args,
            **kwargs
        )

    def execute(self, cmd: str, timeout: int = None) -> Optional[str]:
        """Simple function executes a command on the SSH server
        Returns list of the lines output
        """
        _, stdout, stderr = self.client.exec_command(cmd, timeout=timeout)
        if stdout.channel.recv_exit_status():
            raise CommandException(stderr.read().decode())
        #  if command is executed in the background don't wait for the output
        return (
            None if cmd.rstrip().endswith("&") else stdout.read().decode().rstrip("\n")
        )

    def lines_execute(self, cmd: str, timeout: int = None) -> Optional[list]:
        out = self.execute(cmd, timeout)
        return out.split("\n")


class IPUStorageTerminal(SSHTerminal):
    def __init__(self):
        super().__init__(IPUStorageConfig())
        self.platform = IPUStoragePlatform(self)
        self.docker = Docker(self)


class HostTargetTerminal(SSHTerminal):
    def __init__(self):
        super().__init__(HostTargetConfig())
        self.platform = HostTargetPlatform(self)
        self.docker = Docker(self)


class StorageTargetTerminal(SSHTerminal):
    def __init__(self):
        super().__init__(StorageTargetConfig())
        self.platform = StorageTargetPlatform(self)
        self.docker = Docker(self)
