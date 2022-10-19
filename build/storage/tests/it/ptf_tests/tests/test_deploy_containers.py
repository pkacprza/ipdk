# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#

import os

from ptf.base_tests import BaseTest
from system_tools.const import STORAGE_DIR_PATH

from base import CreateAllTerminalsMixin, DeleteAllContainersMixin, EmptyMixin
from tests.steps.initial import (CloneIPDKRepository, RunCMDSenderContainer,
                                 RunHostTargetContainer,
                                 RunIPUStorageContainer,
                                 RunStorageTargetContainer)


class TestTestPlatforms(CreateAllTerminalsMixin, EmptyMixin, BaseTest):
    def runTest(self):
        # todo set only one time in first time
        self.storage_target_terminal.platform.set_system_setup()
        self.ipu_storage_terminal.platform.set_system_setup()
        self.host_target_terminal.platform.set_system_setup()

        self.storage_target_terminal.platform.check_system_setup()
        self.ipu_storage_terminal.platform.check_system_setup()
        self.host_target_terminal.platform.check_system_setup()


class TestDeployContainers(
    DeleteAllContainersMixin, CreateAllTerminalsMixin, EmptyMixin, BaseTest
):
    def runTest(self):
        clone_step = CloneIPDKRepository(
            self.storage_target_terminal,
            is_teardown=False,
        )
        clone_step.run()

        RunStorageTargetContainer(
            self.storage_target_terminal,
            storage_dir=os.path.join(clone_step.workdir, STORAGE_DIR_PATH),
        ).run()
        RunIPUStorageContainer(
            self.ipu_storage_terminal,
            storage_dir=os.path.join(clone_step.workdir, STORAGE_DIR_PATH),
            shared_dir=os.path.join(clone_step.workdir, "shared"),
        ).run()
        RunHostTargetContainer(
            self.host_target_terminal,
            storage_dir=os.path.join(clone_step.workdir, STORAGE_DIR_PATH),
        ).run()
        RunCMDSenderContainer(
            self.ipu_storage_terminal,
            storage_dir=os.path.join(clone_step.workdir, STORAGE_DIR_PATH),
        ).run()
