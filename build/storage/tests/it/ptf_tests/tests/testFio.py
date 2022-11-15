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


class TestFio1(BaseTest):
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
        fio_dictionary = {
            "mixed_rw_fio": ["randrw", "runtime"],
            "randread_fio": ["randread", "runtime"],
            "sequential_write_fio": ["write", "runtime"],
            "sequential_workload_fio": ["write", "readwrite"],
            "sequential_writetraffic_fio": ["randwrite", "readwrite"],
            "sequential_readtraffic_fio": ["read", "readwrite"],
                          }

    def runTest(self):
        CreateAndExposeSubsystemOverTCPStep(self.storage_target_platform).run()
        volume_id = (
            CreateRamdriveAndAttachAsNsToSubsystemStep(self.storage_target_platform)
                .run()
                .get("ramdrive_id")
        )

        CreateVirtioBlkStep(
            self.host_target_platform,
            self.ipu_storage_platform,
            volume_id,
            self.vm,
        ).run()

        ##Setup or test steps ^?
        _fio_command =(
        f'''$ echo -e $(env -i no_grpc_proxy="" grpc_cli call <host_ip_where_vm_is_run>:50051 \ '''
        f'''RunFio "diskToExercise: { deviceHandle: '$virtio_blk0' } \ '''
        f'''fioArgs: '{\"rw\":\"randrw\", \"runtime\":5, \"numjobs\": 1, \ '''
        f''' \"time_based\": 1, \"group_reporting\": 1 }'") ''')
        _fio_output = self.storage_target_platform.terminal.execute(_fio_command)
        self.assertIn("err= 0", _fio_output)
        self.assertIn("err= Dist stats ", _fio_output)

    def tearDown(self):
        self.storage_target_platform.docker.delete_all_containers()
        self.ipu_storage_platform.docker.delete_all_containers()
        self.host_target_platform.docker.delete_all_containers()
        self.vm.delete()
