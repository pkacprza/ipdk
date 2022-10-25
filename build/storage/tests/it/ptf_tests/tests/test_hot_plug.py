# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#

from ptf.base_tests import BaseTest
from system_tools.test_platform import (HostTargetPlatform, IPUStoragePlatform,
                                        StorageTargetPlatform)
from system_tools.vm import VirtualMachine

from tests.steps.ramdrive import (
    CreateRamdriveAndAttachAsNsToSubsystem64Step,
    CreateRamdriveAndAttachAsNsToSubsystemAbove64Step,
    CreateRamdriveAndAttachAsNsToSubsystemStep)
from tests.steps.subsystem import CreateAndExposeSubsystemOverTCPStep
from tests.steps.virtio_blk import (CreateVirtioBlk64Step,
                                    CreateVirtioBlkAbove64Step,
                                    CreateVirtioBlkStep, DeleteVirtioBlk64Step,
                                    DeleteVirtioBlkStep)


class Test1HotPlug(BaseTest):
    def setUp(self):
        self.storage_target_platform = StorageTargetPlatform()
        self.ipu_storage_platform = IPUStoragePlatform()
        self.host_target_platform = HostTargetPlatform()

        self.vm = VirtualMachine(self.host_target_platform)

        self.storage_target_platform.run_storage_target_container()
        self.ipu_storage_platform.run_ipu_storage_container(
            self.host_target_platform.terminal.config.vm_share_dir_path
        )
        self.host_target_platform.run_host_target_container()
        self.ipu_storage_platform.run_cmd_sender()

        self.vm.run("root", "root")

    def runTest(self):
        CreateAndExposeSubsystemOverTCPStep(self.storage_target_platform).run()
        volume_id = (
            CreateRamdriveAndAttachAsNsToSubsystemStep(self.storage_target_platform)
            .run()
            .get("ramdrive_id")
        )
        device_handle = (
            CreateVirtioBlkStep(
                self.host_target_platform,
                self.ipu_storage_platform,
                volume_id,
                self.vm,
            )
            .run()
            .get("device_handle")
        )
        DeleteVirtioBlkStep(
            self.host_target_platform,
            self.ipu_storage_platform,
            device_handle,
            self.vm,
        ).run()

    def tearDown(self):
        self.storage_target_platform.docker.delete_all_containers()
        self.ipu_storage_platform.docker.delete_all_containers()
        self.host_target_platform.docker.delete_all_containers()
        self.vm.delete()


class Test64HotPlug(BaseTest):
    def setUp(self):
        self.storage_target_platform = StorageTargetPlatform()
        self.ipu_storage_platform = IPUStoragePlatform()
        self.host_target_platform = HostTargetPlatform()

        self.vm = VirtualMachine(self.host_target_platform)

        self.storage_target_platform.run_storage_target_container()
        self.ipu_storage_platform.run_ipu_storage_container(
            self.host_target_platform.terminal.config.vm_share_dir_path
        )
        self.host_target_platform.run_host_target_container()
        self.ipu_storage_platform.run_cmd_sender()

        self.vm.run("root", "root")

    def runTest(self):
        CreateAndExposeSubsystemOverTCPStep(self.storage_target_platform).run()
        volume_ids = (
            CreateRamdriveAndAttachAsNsToSubsystem64Step(self.storage_target_platform)
            .run()
            .get("volume_ids")
        )
        device_handles = (
            CreateVirtioBlk64Step(
                self.host_target_platform,
                self.ipu_storage_platform,
                volume_ids,
                self.vm,
            )
            .run()
            .get("device_handles")
        )
        DeleteVirtioBlk64Step(
            self.host_target_platform,
            self.ipu_storage_platform,
            device_handles,
            self.vm,
        ).run()

    def tearDown(self):
        self.storage_target_platform.docker.delete_all_containers()
        self.ipu_storage_platform.docker.delete_all_containers()
        self.host_target_platform.docker.delete_all_containers()
        self.vm.delete()


class TestAbove64HotPlug(BaseTest):
    def setUp(self):
        self.storage_target_platform = StorageTargetPlatform()
        self.ipu_storage_platform = IPUStoragePlatform()
        self.host_target_platform = HostTargetPlatform()

        self.vm = VirtualMachine(self.host_target_platform)

        self.storage_target_platform.run_storage_target_container()
        self.ipu_storage_platform.run_ipu_storage_container(
            self.host_target_platform.terminal.config.vm_share_dir_path
        )
        self.host_target_platform.run_host_target_container()
        self.ipu_storage_platform.run_cmd_sender()

        self.vm.run("root", "root")

    def runTest(self):
        CreateAndExposeSubsystemOverTCPStep(self.storage_target_platform).run()
        volume_ids = (
            CreateRamdriveAndAttachAsNsToSubsystemAbove64Step(
                self.storage_target_platform
            )
            .run()
            .get("volume_ids")
        )
        with self.assertRaises(Exception):
            CreateVirtioBlkAbove64Step(
                self.host_target_platform,
                self.ipu_storage_platform,
                volume_ids,
                self.vm,
            ).run().get("device_handles")

    def tearDown(self):
        self.storage_target_platform.docker.delete_all_containers()
        self.ipu_storage_platform.docker.delete_all_containers()
        self.host_target_platform.docker.delete_all_containers()
        self.vm.delete()
