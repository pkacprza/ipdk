# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#

from system_tools.test_platform import (BaseTestPlatform, HostTargetPlatform,
                                        IPUStoragePlatform,
                                        StorageTargetPlatform)
from tests.steps.base import TestStep


class CloneIPDKRepository(TestStep):
    """Clone ipdk repository"""

    def __init__(
        self,
        platform: BaseTestPlatform,
        is_teardown: bool,
        repository_url: str = "'https://github.com/ipdk-io/ipdk.git'",
        branch: str = "main",
    ) -> None:
        """
        Assumption: In workdir folder You can't have any important files
        All files will be deleted
        """
        super().__init__(platform, is_teardown)
        self.repository_url = repository_url
        self.branch = branch

    def _prepare(self):
        self.platform.terminal.execute(
            f"sudo rm -rf {self.platform.terminal.config.workdir}"
        )
        self.platform.terminal.execute(f"mkdir {self.platform.terminal.config.workdir}")

    # TODO: init submodules
    def _step(self):
        cmd = f"cd {self.platform.terminal.config.workdir} && git clone --branch {self.branch} {self.repository_url}"
        self.platform.terminal.execute(cmd)

    def _assertion_after_step(self):
        self.platform.terminal.execute(
            f"ls {self.platform.terminal.config.workdir}/ipdk/build"
        )
        self.platform.terminal.execute(
            f"cd {self.platform.terminal.config.workdir}/ipdk/build/storage && git log"
        )


class RunStorageTargetContainer(TestStep):
    def __init__(
        self,
        platform: StorageTargetPlatform,
        is_teardown: bool = False,
    ) -> None:
        super().__init__(platform, is_teardown)

    def _step(self):
        self.platform.run_storage_target_container()

    def _assertion_after_step(self):
        out = self.platform.terminal.execute("docker ps")
        assert "storage-target" in out


class RunIPUStorageContainer(TestStep):
    def __init__(
        self,
        platform: IPUStoragePlatform,
        shared_dir: str,
        is_teardown: bool = False,
    ) -> None:
        super().__init__(platform, is_teardown)
        self.shared_dir = shared_dir

    def _prepare(self):
        self.platform.terminal.client.exec_command(f"mkdir -p {self.shared_dir}")

    def _step(self):
        self.platform.run_ipu_storage_container(self.shared_dir)

    def _assertion_after_step(self):
        out = self.platform.terminal.execute("docker ps")
        assert "ipu-storage-container" in out


class RunHostTargetContainer(TestStep):
    def __init__(self, platform: HostTargetPlatform, is_teardown: bool = False) -> None:
        super().__init__(platform, is_teardown)

    def _step(self):
        self.platform.run_host_target_container()

    def _assertion_after_step(self):
        # it's ok but container stops after few seconds
        out = self.platform.terminal.execute("docker ps -a")
        assert "host-target" in out


class RunCMDSenderContainer(TestStep):
    def __init__(
        self,
        platform: IPUStoragePlatform,
        is_teardown: bool = False,
    ) -> None:
        super().__init__(platform, is_teardown)

    def _step(self):
        self.platform.run_cmd_sender()

    def _assertion_after_step(self):
        out = self.platform.terminal.execute("docker ps").splitlines()
        is_container = False
        for line in out:
            if "cmd-sender" in line:
                is_container = True
        assert is_container
