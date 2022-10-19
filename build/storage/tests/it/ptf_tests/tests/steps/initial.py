# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#

from system_tools.ssh_terminal import SSHTerminal
from tests.steps.base import TestStep


class CloneIPDKRepository(TestStep):
    """Clone ipdk repository"""

    def __init__(
        self,
        terminal: SSHTerminal,
        is_teardown: bool,
        repository_url: str = "'https://github.com/ipdk-io/ipdk.git'",
        branch: str = "main",
        workdir: str = None,
    ) -> None:
        """
        Assumption: In workdir folder You can't have any important files
        All files will be deleted
        """
        super().__init__(terminal, is_teardown)
        self.repository_url = repository_url
        self.branch = branch
        self.workdir = workdir or f"/home/{terminal.config.username}/ipdk_tests_workdir"

    def _prepare(self):
        self.terminal.execute(f"sudo rm -rf {self.workdir}")
        self.terminal.execute(f"mkdir {self.workdir}")

    # TODO: init submodules
    def _step(self):
        cmd = f"cd {self.workdir} && git clone --branch {self.branch} {self.repository_url}"
        self.terminal.execute(cmd)

    def _assertion_after_step(self):
        self.terminal.execute(f"ls {self.workdir}/ipdk/build")
        self.terminal.execute(f"cd {self.workdir}/ipdk/build/storage && git log")


class RunStorageTargetContainer(TestStep):
    def __init__(
        self, terminal: SSHTerminal, storage_dir: str, is_teardown: bool = False
    ) -> None:
        super().__init__(terminal, is_teardown)
        self.storage_dir = storage_dir

    def _step(self):
        self.terminal.platform.run_storage_target_container(self.storage_dir)

    def _assertion_after_step(self):
        out = self.terminal.execute("docker ps")
        assert "storage-target" in out


class RunIPUStorageContainer(TestStep):
    def __init__(
        self,
        terminal: SSHTerminal,
        storage_dir: str,
        shared_dir: str,
        is_teardown: bool = False,
    ) -> None:
        super().__init__(terminal, is_teardown)
        self.storage_dir = storage_dir
        self.shared_dir = shared_dir

    def _prepare(self):
        self.terminal.client.exec_command(f"mkdir -p {self.shared_dir}")

    def _step(self):
        self.terminal.platform.run_ipu_storage_container(
            self.storage_dir, self.shared_dir
        )

    def _assertion_after_step(self):
        out = self.terminal.execute("docker ps")
        assert "ipu-storage-container" in out


class RunHostTargetContainer(TestStep):
    def __init__(
        self, terminal: SSHTerminal, storage_dir: str, is_teardown: bool = False
    ) -> None:
        super().__init__(terminal, is_teardown)
        self.storage_dir = storage_dir

    def _step(self):
        self.terminal.platform.run_host_target_container(self.storage_dir)

    def _assertion_after_step(self):
        # it's ok but container stops after few seconds
        out = self.terminal.execute("docker ps -a")
        assert "host-target" in out


class RunCMDSenderContainer(TestStep):
    def __init__(
        self,
        terminal: SSHTerminal,
        storage_dir: str,
        is_teardown: bool = False,
    ) -> None:
        super().__init__(terminal, is_teardown)
        self.storage_dir = storage_dir

    def _step(self):
        self.terminal.platform.run_cmd_sender(self.storage_dir)

    def _assertion_after_step(self):
        out = self.terminal.lines_execute("docker ps")
        is_container = False
        for line in out:
            if "cmd-sender" in line:
                is_container = True
        assert is_container
