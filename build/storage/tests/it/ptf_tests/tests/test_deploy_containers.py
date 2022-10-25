# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#

import os

from ptf.base_tests import BaseTest
from system_tools.test_platform import (HostTargetPlatform, IPUStoragePlatform,
                                        StorageTargetPlatform)

from tests.steps.initial import (CloneIPDKRepository, RunCMDSenderContainer,
                                 RunHostTargetContainer,
                                 RunIPUStorageContainer,
                                 RunStorageTargetContainer)


class TestTestPlatforms(BaseTest):
    def setUp(self):
        self.storage_target_platform = StorageTargetPlatform()
        self.ipu_storage_platform = IPUStoragePlatform()
        self.host_target_platform = HostTargetPlatform()

    def runTest(self):
        # todo set only one time in first time
        self.storage_target_platform.set_system_setup()
        self.ipu_storage_platform.set_system_setup()
        self.host_target_platform.set_system_setup()

        self.storage_target_platform.check_system_setup()
        self.ipu_storage_platform.check_system_setup()
        self.host_target_platform.check_system_setup()

    def tearDown(self):
        pass


class TestDeployContainers(BaseTest):
    def setUp(self):
        self.storage_target_platform = StorageTargetPlatform()
        self.ipu_storage_platform = IPUStoragePlatform()
        self.host_target_platform = HostTargetPlatform()

    def runTest(self):
        clone_step = CloneIPDKRepository(
            self.storage_target_platform,
            is_teardown=False,
        )
        clone_step.run()

        RunStorageTargetContainer(self.storage_target_platform).run()
        RunIPUStorageContainer(
            self.ipu_storage_platform,
            shared_dir=os.path.join(
                self.host_target_platform.terminal.config.vm_share_dir_path, "shared"
            ),
        ).run()
        RunHostTargetContainer(self.host_target_platform).run()
        RunCMDSenderContainer(self.ipu_storage_platform).run()

    def tearDown(self):
        self.storage_target_platform.docker.delete_all_containers()
        self.ipu_storage_platform.docker.delete_all_containers()
        self.host_target_platform.docker.delete_all_containers()
