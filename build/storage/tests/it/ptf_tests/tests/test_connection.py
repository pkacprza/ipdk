# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#

from ptf.base_tests import BaseTest

from base import CreateAllTerminalsMixin, EmptyMixin


class TestTerminalConnect(CreateAllTerminalsMixin, EmptyMixin, BaseTest):
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


class TestTerminalConnectHasRootPrivilegnes(
    CreateAllTerminalsMixin, EmptyMixin, BaseTest
):
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
