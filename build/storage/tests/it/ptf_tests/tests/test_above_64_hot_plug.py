# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#

import sys

sys.path.append("../../..")

from ptf.base_tests import BaseTest

from base import (CreateAllTerminalsMixin, DeleteAllContainersMixin,
                  DeleteVMMixin, EmptyMixin, RunAllContainersMixin, RunVMMixin)
from tests.steps.ramdrive import \
    CreateRamdriveAndAttachAsNsToSubsystemAbove64Step
from tests.steps.subsystem import CreateAndExposeSubsystemOverTCPStep
from tests.steps.virtio_blk import CreateVirtioBlkAbove64Step


class TestCreateAndExposeSubsystemOverTCP3(RunAllContainersMixin, EmptyMixin, BaseTest):
    def runTest(self):
        CreateAndExposeSubsystemOverTCPStep(self.storage_target_terminal).run()


class TestCreateRamdriveAndAttachAsNsToSubsystemAbove64(
    CreateAllTerminalsMixin, EmptyMixin, BaseTest
):

    VOLUME_IDS = []

    def runTest(self):
        volume_ids = CreateRamdriveAndAttachAsNsToSubsystemAbove64Step(
            self.storage_target_terminal
        ).run()
        TestCreateRamdriveAndAttachAsNsToSubsystemAbove64.VOLUME_IDS = volume_ids


class TestCreateVirtioBlkAbove64(
    DeleteVMMixin, DeleteAllContainersMixin, RunVMMixin, EmptyMixin, BaseTest
):

    DEVICE_HANDLES = []

    def runTest(self):
        TestCreateVirtioBlkAbove64.DEVICE_HANDLES = CreateVirtioBlkAbove64Step(
            self.ipu_storage_terminal,
            TestCreateRamdriveAndAttachAsNsToSubsystemAbove64.VOLUME_IDS,
            self.ipu_storage_terminal.platform.vm,
        ).run()
