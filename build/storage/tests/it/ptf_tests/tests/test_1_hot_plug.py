# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#

import sys

sys.path.append("../../..")

from ptf.base_tests import BaseTest

from base import (CreateAllTerminalsMixin, DeleteAllContainersMixin,
                  DeleteVMMixin, EmptyMixin, RunAllContainersMixin, RunVMMixin)
from tests.steps.ramdrive import CreateRamdriveAndAttachAsNsToSubsystemStep
from tests.steps.subsystem import CreateAndExposeSubsystemOverTCPStep
from tests.steps.virtio_blk import CreateVirtioBlkStep, DeleteVirtioBlkStep


class TestCreateAndExposeSubsystemOverTCP(RunAllContainersMixin, EmptyMixin, BaseTest):
    def runTest(self):
        CreateAndExposeSubsystemOverTCPStep(self.storage_target_terminal).run()


class TestCreateRamdriveAndAttachAsNsToSubsystem(
    CreateAllTerminalsMixin, EmptyMixin, BaseTest
):

    VOLUME_ID = []

    def runTest(self):
        volume_id = CreateRamdriveAndAttachAsNsToSubsystemStep(
            self.storage_target_terminal
        ).run()
        TestCreateRamdriveAndAttachAsNsToSubsystem.VOLUME_ID = volume_id


class TestCreateVirtioBlk(RunVMMixin, EmptyMixin, BaseTest):

    DEVICE_HANDLE = []

    def runTest(self):
        TestCreateVirtioBlk.DEVICE_HANDLE = CreateVirtioBlkStep(
            self.ipu_storage_terminal,
            TestCreateRamdriveAndAttachAsNsToSubsystem.VOLUME_ID,
            self.ipu_storage_terminal.platform.vm,
        ).run()


class TestDeleteVirtioBlk(
    DeleteVMMixin,
    DeleteAllContainersMixin,
    CreateAllTerminalsMixin,
    EmptyMixin,
    BaseTest,
):
    def runTest(self):
        DeleteVirtioBlkStep(
            self.ipu_storage_terminal,
            TestCreateVirtioBlk.DEVICE_HANDLE,
            self.ipu_storage_terminal.platform.vm,
        ).run()
