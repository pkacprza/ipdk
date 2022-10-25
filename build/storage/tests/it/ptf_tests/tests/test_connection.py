# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#

from ptf.base_tests import BaseTest
from system_tools.test_platform import (HostTargetPlatform, IPUStoragePlatform,
                                        StorageTargetPlatform)


class TestTerminalConnect(BaseTest):
    def setUp(self):
        self.storage_target_platform = StorageTargetPlatform()
        self.ipu_storage_platform = IPUStoragePlatform()
        self.host_target_platform = HostTargetPlatform()

    def runTest(self):
        self.assertEqual(
            self.storage_target_platform.terminal.execute("whoami"),
            self.storage_target_platform.terminal.config.username,
        )
        self.assertEqual(
            self.ipu_storage_platform.terminal.execute("whoami"),
            self.ipu_storage_platform.terminal.config.username,
        )
        self.assertEqual(
            self.host_target_platform.terminal.execute("whoami"),
            self.host_target_platform.terminal.config.username,
        )

    def tearDown(self):
        pass


class TestTerminalConnectHasRootPrivilegnes(BaseTest):
    def setUp(self):
        self.storage_target_platform = StorageTargetPlatform()
        self.ipu_storage_platform = IPUStoragePlatform()
        self.host_target_platform = HostTargetPlatform()

    def runTest(self):
        self.assertEqual(
            self.storage_target_platform.terminal.execute("sudo whoami"),
            "root",
        )
        self.assertEqual(
            self.ipu_storage_platform.terminal.execute("sudo whoami"),
            "root",
        )
        self.assertEqual(
            self.host_target_platform.terminal.execute("sudo whoami"),
            "root",
        )

    def tearDown(self):
        pass
