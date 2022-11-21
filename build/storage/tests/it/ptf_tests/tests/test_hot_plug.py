# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#

from ptf.base_tests import BaseTest

from system_tools import vm
from system_tools.test_platform import (HostTargetPlatform, IPUStoragePlatform,
                                        StorageTargetPlatform)
from system_tools.docker import Docker
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
        self.docker = Docker(self.storage_target_platform.terminal)

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
                vm,
            )
            .run()
            .get("device_handles")
        )
        DeleteVirtioBlkStep(
            self.host_target_platform,
            self.ipu_storage_platform,
            device_handles,
            vm,
        ).run()
        cmd_sender_id = self.docker.get_docker_containers_id_from_docker_image_name(
            "cmd-sender"
        )[0]
        self.host_target_platform.terminal.execute(
            f"""docker exec {cmd_sender_id} """
            f"""echo (cookie)"""
            # f'''$ echo -e $(env -i no_grpc_proxy="" grpc_cli call {self.host_target_platform.terminal.config.ip_address}:50051 \ '''
            # f'''RunFio "diskToExercise: {{ deviceHandle: '$virtio_blk0' }} \ '''
            # f'''fioArgs: '{{\"rw\":\"readwrite\", \"runtime\":5, \"numjobs\": 1, \ '''
            # f''' \"time_based\": 1, \"group_reporting\": 1 }}'") '''
        )


        #
        # self.assertIn("err= 0", self._fio_output)
        # self.assertIn("Disk stats ", self._fio_output)
    # #
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
