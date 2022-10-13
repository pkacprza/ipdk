# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#

import os
import sys

sys.path.append("../../..")

from ptf.base_tests import BaseTest
from test_connection import BaseTerminalMixin

from tests.steps.subsystem import CreateAndExposeSubsystemOverTCPStep
from tests.steps.ramdrive import (
    CreateRamdriveAndAttachAsNsToSubsystem64Step,
    CreateRamdriveAndAttachAsNsToSubsystemStep,
)
from tests.steps.initial import (
    RunCMDSenderContainer,
    RunHostTargetContainer,
    RunIPUStorageContainer,
    RunStorageTargetContainer,
)

from tests.steps.virtio_blk import (
    CreateVirtioBlk64Step,
    DeleteVirtioBlk64Step,
    CreateVirtioBlkStep,
    DeleteVirtioBlkStep,
)
from system_tools.const import STORAGE_DIR_PATH

class TestCreateAndExposeSubsystemOverTCP(BaseTerminalMixin, BaseTest):

    def setUp(self):
        super().setUp()
        self.ipu_storage_terminal.platform.vm.delete()
        self.storage_target_terminal.delete_all_containers()
        self.ipu_storage_terminal.delete_all_containers()
        self.host_target_terminal.delete_all_containers()
        workdir = f"/home/{self.ipu_storage_terminal.config.username}/ipdk_tests_workdir"
        RunStorageTargetContainer(
            self.storage_target_terminal,
            storage_dir=os.path.join(workdir, STORAGE_DIR_PATH),
        ).run()
        RunIPUStorageContainer(
            self.ipu_storage_terminal,
            storage_dir=os.path.join(workdir, STORAGE_DIR_PATH),
            shared_dir=os.path.join(workdir, "shared"),
        ).run()
        RunHostTargetContainer(
            self.host_target_terminal,
            storage_dir=os.path.join(workdir, STORAGE_DIR_PATH),
        ).run()
        RunCMDSenderContainer(
            self.ipu_storage_terminal,
            storage_dir=os.path.join(workdir, STORAGE_DIR_PATH),
        ).run()

    def runTest(self):
        CreateAndExposeSubsystemOverTCPStep(self.storage_target_terminal).run()

class TestCreateRamdriveAndAttachAsNsToSubsystem64(BaseTerminalMixin, BaseTest):

    VOLUME_IDS = []

    def runTest(self):
        volume_ids = CreateRamdriveAndAttachAsNsToSubsystem64Step(
            self.storage_target_terminal
        ).run()
        TestCreateRamdriveAndAttachAsNsToSubsystem64.VOLUME_IDS = volume_ids


class TestCreateVirtioBlk64(BaseTerminalMixin, BaseTest):

    DEVICE_HANDLES = []

    def setUp(self):
        super().setUp()
        self.ipu_storage_terminal.platform.vm.run("root", "root")

    def runTest(self):
        TestCreateVirtioBlk64.DEVICE_HANDLES = CreateVirtioBlk64Step(
            self.ipu_storage_terminal,
            TestCreateRamdriveAndAttachAsNsToSubsystem64.VOLUME_IDS,
            self.ipu_storage_terminal.platform.vm,
        ).run()


class TestDeleteVirtioBlk64(BaseTerminalMixin, BaseTest):
    def runTest(self):
        DeleteVirtioBlk64Step(
            self.ipu_storage_terminal,
            TestCreateVirtioBlk64.DEVICE_HANDLES,
            self.ipu_storage_terminal.platform.vm,
        ).run()

    def tearDown(self):
        self.ipu_storage_terminal.platform.vm.delete()
        self.storage_target_terminal.delete_all_containers()
        self.ipu_storage_terminal.delete_all_containers()
        self.host_target_terminal.delete_all_containers()





class TestCreateAndExposeSubsystemOverTCP2(BaseTerminalMixin, BaseTest):
    def setUp(self):
        super().setUp()
        self.ipu_storage_terminal.platform.vm.delete()
        self.storage_target_terminal.delete_all_containers()
        self.ipu_storage_terminal.delete_all_containers()
        self.host_target_terminal.delete_all_containers()
        workdir = f"/home/{self.ipu_storage_terminal.config.username}/ipdk_tests_workdir"
        RunStorageTargetContainer(
            self.storage_target_terminal,
            storage_dir=os.path.join(workdir, STORAGE_DIR_PATH),
        ).run()
        RunIPUStorageContainer(
            self.ipu_storage_terminal,
            storage_dir=os.path.join(workdir, STORAGE_DIR_PATH),
            shared_dir=os.path.join(workdir, "shared"),
        ).run()
        RunHostTargetContainer(
            self.host_target_terminal,
            storage_dir=os.path.join(workdir, STORAGE_DIR_PATH),
        ).run()
        RunCMDSenderContainer(
            self.ipu_storage_terminal,
            storage_dir=os.path.join(workdir, STORAGE_DIR_PATH),
        ).run()

    def runTest(self):
        CreateAndExposeSubsystemOverTCPStep(self.storage_target_terminal).run()


class TestCreateRamdriveAndAttachAsNsToSubsystem(BaseTerminalMixin, BaseTest):

    VOLUME_ID = []

    def runTest(self):
        volume_id = CreateRamdriveAndAttachAsNsToSubsystemStep(
            self.storage_target_terminal
        ).run()
        TestCreateRamdriveAndAttachAsNsToSubsystem.VOLUME_ID = volume_id


class TestCreateVirtioBlk(BaseTerminalMixin, BaseTest):

    DEVICE_HANDLE = []

    def setUp(self):
        super().setUp()
        self.ipu_storage_terminal.platform.vm.run("root", "root")

    def runTest(self):
        TestCreateVirtioBlk.DEVICE_HANDLE = CreateVirtioBlkStep(
            self.ipu_storage_terminal,
            TestCreateRamdriveAndAttachAsNsToSubsystem.VOLUME_ID,
            self.ipu_storage_terminal.platform.vm,
        ).run()


class TestDeleteVirtioBlk(BaseTerminalMixin, BaseTest):
    def runTest(self):
        DeleteVirtioBlkStep(
            self.ipu_storage_terminal,
            TestCreateVirtioBlk.DEVICE_HANDLE,
            self.ipu_storage_terminal.platform.vm,
        ).run()

    def tearDown(self):
        self.ipu_storage_terminal.platform.vm.delete()
