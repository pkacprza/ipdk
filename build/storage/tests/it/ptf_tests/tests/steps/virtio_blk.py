# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#

from tests.steps.base import TestStep


class CreateVirtioBlk64Step(TestStep):
    def __init__(
        self, host_target_platform, ipu_platform, volume_ids, vm, is_teardown=False
    ):
        super().__init__(host_target_platform, is_teardown)
        self.volume_ids = volume_ids
        self.vm = vm
        self.ipu_platform = ipu_platform

    def _assertions_before_step(self):
        assert self.vm.get_number_of_virtio_blk_devices() == 0
        # todo check if vm is running properly

    def _step(self):
        device_handles = []
        for physical_id, volume_id in enumerate(self.volume_ids):
            device_handle = self.ipu_platform.create_virtio_blk_device(
                volume_id, physical_id
            )
            device_handles.append(device_handle)
        self.result["device_handles"] = device_handles

    def _assertion_after_step(self):
        assert self.vm.get_number_of_virtio_blk_devices() == 64


class DeleteVirtioBlk64Step(TestStep):
    def __init__(
        self, host_target_platform, ipu_platform, device_handles, vm, is_teardown=False
    ):
        super().__init__(host_target_platform, is_teardown)
        self.device_handles = device_handles
        self.vm = vm
        self.ipu_platform = ipu_platform

    def _assertions_before_step(self):
        assert self.vm.get_number_of_virtio_blk_devices() == 64
        # todo check if vm is running properly

    def _step(self):
        for device_handle in self.device_handles:
            self.ipu_platform.delete_virtio_blk_device(device_handle)

    def _assertion_after_step(self):
        assert self.vm.get_number_of_virtio_blk_devices() == 0


class CreateVirtioBlkStep(TestStep):
    def __init__(
        self, host_target_platform, ipu_platform, volume_id, vm, is_teardown=False
    ):
        super().__init__(host_target_platform, is_teardown)
        self.volume_id = volume_id
        self.vm = vm
        self.ipu_platform = ipu_platform

    def _assertions_before_step(self):
        assert self.vm.get_number_of_virtio_blk_devices() == 0
        # todo check if vm is running properly

    def _step(self):
        self.result["device_handle"] = self.ipu_platform.create_virtio_blk_device(
            self.volume_id, 0
        )
        _fio_command = (
            f'''$ echo -e $(env -i no_grpc_proxy="" grpc_cli call {self.host_target_platform.terminal.config.ip_address}:50051 \ '''
            f'''RunFio "diskToExercise: {{ deviceHandle: '$virtio_blk0' }} \ '''
            f'''fioArgs: '{{\"rw\":\"readwrite\", \"runtime\":5, \"numjobs\": 1, \ '''
            f''' \"time_based\": 1, \"group_reporting\": 1 }}'") ''')
        self._fio_output = self.storage_target_platform.terminal.execute(_fio_command)

    def _assertion_after_step(self):
        assert self.vm.get_number_of_virtio_blk_devices() == 1
        self.assertIn("err= 0", self._fio_output)
        self.assertIn("Disk stats ", self._fio_output)

class DeleteVirtioBlkStep(TestStep):
    def __init__(
        self, host_target_platform, ipu_platform, device_handle, vm, is_teardown=False
    ):
        super().__init__(host_target_platform, is_teardown)
        self.device_handle = device_handle
        self.vm = vm
        self.ipu_platform = ipu_platform

    # def _assertions_before_step(self):
    #     assert self.vm.get_number_of_virtio_blk_devices() == 1
    #     # todo check if vm is running properly
    #
    # def _step(self):
    #     self.ipu_platform.delete_virtio_blk_device(self.device_handle)
    #
    # def _assertion_after_step(self):
    #     assert self.vm.get_number_of_virtio_blk_devices() == 0


class CreateVirtioBlkAbove64Step(TestStep):
    def __init__(
        self, host_target_platform, ipu_platform, volume_ids, vm, is_teardown=False
    ):
        super().__init__(host_target_platform, is_teardown)
        self.volume_ids = volume_ids
        self.vm = vm
        self.host_target_platform = host_target_platform
        self.ipu_platform = ipu_platform

    def _assertions_before_step(self):
        assert len(self.volume_ids) > 64
        assert self.vm.get_number_of_virtio_blk_devices() == 0
        # todo check if vm is running properly

    def _step(self):
        device_handles = []
        for physical_id, volume_id in enumerate(self.volume_ids):
            device_handle = self.ipu_platform.create_virtio_blk_device(
                volume_id, physical_id
            )
            device_handles.append(device_handle)
        self.result["device_handles"] = device_handles

    def _assertion_after_step(self):
        assert self.vm.get_number_of_virtio_blk_devices() > 64
