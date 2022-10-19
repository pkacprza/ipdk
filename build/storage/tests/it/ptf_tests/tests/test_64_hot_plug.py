# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#

import sys

sys.path.append("../../..")

from ptf.base_tests import BaseTest

from base import (CreateAllTerminalsMixin, DeleteAllContainersMixin,
                  DeleteVMMixin, EmptyMixin, RunAllContainersMixin, RunVMMixin)
from tests.steps.ramdrive import CreateRamdriveAndAttachAsNsToSubsystem64Step
from tests.steps.subsystem import CreateAndExposeSubsystemOverTCPStep
from tests.steps.virtio_blk import CreateVirtioBlk64Step, DeleteVirtioBlk64Step


class TestCreateAndExposeSubsystemOverTCP(RunAllContainersMixin, EmptyMixin, BaseTest):
    def runTest(self):
        CreateAndExposeSubsystemOverTCPStep(self.storage_target_terminal).run()


class TestCreateRamdriveAndAttachAsNsToSubsystem64(
    CreateAllTerminalsMixin, EmptyMixin, BaseTest
):

    VOLUME_IDS = []

    def runTest(self):
        volume_ids = CreateRamdriveAndAttachAsNsToSubsystem64Step(
            self.storage_target_terminal
        ).run()
        TestCreateRamdriveAndAttachAsNsToSubsystem64.VOLUME_IDS = volume_ids


class TestCreateVirtioBlk64(RunVMMixin, EmptyMixin, BaseTest):

    DEVICE_HANDLES = []

    def runTest(self):
        TestCreateVirtioBlk64.DEVICE_HANDLES = CreateVirtioBlk64Step(
            self.ipu_storage_terminal,
            TestCreateRamdriveAndAttachAsNsToSubsystem64.VOLUME_IDS,
            self.ipu_storage_terminal.platform.vm,
        ).run()


class TestDeleteVirtioBlk64(
    DeleteVMMixin,
    DeleteAllContainersMixin,
    CreateAllTerminalsMixin,
    EmptyMixin,
    BaseTest,
):
    def runTest(self):
        DeleteVirtioBlk64Step(
            self.ipu_storage_terminal,
            TestCreateVirtioBlk64.DEVICE_HANDLES,
            self.ipu_storage_terminal.platform.vm,
        ).run()
