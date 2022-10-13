# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#

from ptf.base_tests import BaseTest

from system_tools.ssh_terminal import (
    HostTargetTerminal,
    IPUStorageTerminal,
    StorageTargetTerminal,
)


class BaseTerminalMixin:
    def setUp(self):
        self.storage_target_terminal = StorageTargetTerminal()
        self.ipu_storage_terminal = IPUStorageTerminal()
        self.host_target_terminal = HostTargetTerminal()

    def tearDown(self):
        pass


class TestTerminalConnect(BaseTerminalMixin, BaseTest):
    def runTest(self):
        self.assertEqual(
            self.storage_target_terminal.execute("whoami"),
            self.storage_target_terminal.config.username,
        )
        self.assertEqual(
            self.ipu_storage_terminal.execute("whoami"),
            self.ipu_storage_terminal.config.username,
        )
        self.assertEqual(
            self.host_target_terminal.execute("whoami"),
            self.host_target_terminal.config.username,
        )


class TestTerminalConnectHasRootPrivilegnes(BaseTerminalMixin, BaseTest):
    def runTest(self):
        self.assertEqual(
            self.storage_target_terminal.execute("sudo whoami"),
            "root",
        )
        self.assertEqual(
            self.ipu_storage_terminal.execute("sudo whoami"),
            "root",
        )
        self.assertEqual(
            self.host_target_terminal.execute("sudo whoami"),
            "root",
        )
