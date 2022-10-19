# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#

import os

from system_tools.const import STORAGE_DIR_PATH
from system_tools.ssh_terminal import (HostTargetTerminal, IPUStorageTerminal,
                                       StorageTargetTerminal)

from tests.steps.initial import (RunCMDSenderContainer, RunHostTargetContainer,
                                 RunIPUStorageContainer,
                                 RunStorageTargetContainer)


class EmptyMixin:
    def setUp(self):
        pass

    def tearDown(self):
        pass


class CreateAllTerminalsMixin:
    def setUp(self):
        self.storage_target_terminal = StorageTargetTerminal()
        self.ipu_storage_terminal = IPUStorageTerminal()
        self.host_target_terminal = HostTargetTerminal()


class DeleteAllContainersMixin:
    def tearDown(self):
        super().tearDown()
        self.storage_target_terminal.docker.delete_all_containers()
        self.ipu_storage_terminal.docker.delete_all_containers()
        self.host_target_terminal.docker.delete_all_containers()


class RunAllContainersMixin(CreateAllTerminalsMixin):
    def setUp(self):
        super().setUp()
        workdir = (
            f"/home/{self.ipu_storage_terminal.config.username}/ipdk_tests_workdir"
        )
        storage_dir = os.path.join(workdir, STORAGE_DIR_PATH)
        shared_dir = os.path.join(workdir, "shared")

        self.storage_target_terminal.platform.run_storage_target_container(storage_dir)
        self.ipu_storage_terminal.platform.run_ipu_storage_container(
            storage_dir, shared_dir
        )
        self.host_target_terminal.platform.run_host_target_container(storage_dir)
        self.ipu_storage_terminal.platform.run_cmd_sender(storage_dir)


class RunVMMixin(CreateAllTerminalsMixin):
    def setUp(self):
        super().setUp()
        self.ipu_storage_terminal.platform.vm.run("root", "root")


class DeleteVMMixin:
    def tearDown(self):
        super().tearDown()
        self.ipu_storage_terminal.platform.vm.delete()
