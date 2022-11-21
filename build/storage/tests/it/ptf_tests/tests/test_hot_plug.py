# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#

from ptf.base_tests import BaseTest
from system_tools.test_platform import (HostTargetPlatform, IPUStoragePlatform,
                                        StorageTargetPlatform)

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

    def runTest(self):
        CreateAndExposeSubsystemOverTCPStep(self.storage_target_platform).run()
        volume_ids = (
            CreateRamdriveAndAttachAsNsToSubsystemStep(self.storage_target_platform)
            .run()
            .get("volume_ids")
        )
        device_handles = (
            CreateVirtioBlkStep(
                self.host_target_platform,
                self.ipu_storage_platform,
                volume_ids,
            )
            .run()
            .get("device_handles")
        )
        DeleteVirtioBlkStep(
            self.host_target_platform,
            self.ipu_storage_platform,
            device_handles,
        ).run()
    #
    # def tearDown(self):
    #     self.storage_target_platform.clean()
    #     self.host_target_platform.clean()
    #     self.ipu_storage_platform.clean()


# class Test64HotPlug(BaseTest):
#     def setUp(self):
#         self.storage_target_platform = StorageTargetPlatform()
#         self.ipu_storage_platform = IPUStoragePlatform()
#         self.host_target_platform = HostTargetPlatform()
#
#     def runTest(self):
#         CreateAndExposeSubsystemOverTCPStep(self.storage_target_platform).run()
#         volume_ids = (
#             CreateRamdriveAndAttachAsNsToSubsystem64Step(self.storage_target_platform)
#             .run()
#             .get("volume_ids")
#         )
#         device_handles = (
#             CreateVirtioBlk64Step(
#                 self.host_target_platform,
#                 self.ipu_storage_platform,
#                 volume_ids,
#             )
#             .run()
#             .get("device_handles")
#         )
#         DeleteVirtioBlk64Step(
#             self.host_target_platform,
#             self.ipu_storage_platform,
#             device_handles,
#         ).run()
#
#     def tearDown(self):
#         self.storage_target_platform.clean()
#         self.host_target_platform.clean()
#         self.ipu_storage_platform.clean()
#
#
# class TestAbove64HotPlug(BaseTest):
#     def setUp(self):
#         self.storage_target_platform = StorageTargetPlatform()
#         self.ipu_storage_platform = IPUStoragePlatform()
#         self.host_target_platform = HostTargetPlatform()
#
#     def runTest(self):
#         CreateAndExposeSubsystemOverTCPStep(self.storage_target_platform).run()
#         volume_ids = (
#             CreateRamdriveAndAttachAsNsToSubsystemAbove64Step(
#                 self.storage_target_platform
#             )
#             .run()
#             .get("volume_ids")
#         )
#         with self.assertRaises(Exception):
#             CreateVirtioBlkAbove64Step(
#                 self.host_target_platform,
#                 self.ipu_storage_platform,
#                 volume_ids,
#             ).run().get("device_handles")
#
#     def tearDown(self):
#         self.storage_target_platform.clean()
#         self.host_target_platform.clean()
#         self.ipu_storage_platform.clean()
