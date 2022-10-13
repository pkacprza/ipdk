# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#

from tests.steps.base import TestStep


class CreateVirtioBlk64Step(TestStep):
    def __init__(self, terminal, volume_ids, vm, is_teardown=False):
        super().__init__(terminal, is_teardown)
        self.volume_ids = volume_ids
        self.vm = vm

    def _assertions_before_step(self):
        assert self.vm.get_number_of_virtio_blk_devices() == 0
        # todo check if vm is running properly

    def _step(self):
        device_handles = []
        for physical_id, volume_id in enumerate(self.volume_ids):
            device_handle = self.terminal.platform.create_virtio_blk_device(volume_id, physical_id)
            device_handles.append(device_handle)
        self.device_handles = device_handles

    def _assertion_after_step(self):
        assert self.vm.get_number_of_virtio_blk_devices() == 64

    def run(self):
        self._assertions_before_step()
        self._step()
        self._assertion_after_step()
        return self.device_handles


class DeleteVirtioBlk64Step(TestStep):
    def __init__(self, terminal, device_handles, vm, is_teardown=False):
        super().__init__(terminal, is_teardown)
        self.device_handles = device_handles
        self.vm = vm

    def _assertions_before_step(self):
        assert self.vm.get_number_of_virtio_blk_devices() == 64
        # todo check if vm is running properly

    def _step(self):
        for device_handle in self.device_handles:
            self.terminal.platform.delete_virtio_blk_device(device_handle)

    def _assertion_after_step(self):
        assert self.vm.get_number_of_virtio_blk_devices() == 0


class CreateVirtioBlkStep(TestStep):
    def __init__(self, terminal, volume_id, vm, is_teardown=False):
        super().__init__(terminal, is_teardown)
        self.volume_id = volume_id
        self.vm = vm

    def _assertions_before_step(self):
        assert self.vm.get_number_of_virtio_blk_devices() == 0
        # todo check if vm is running properly

    def _step(self):
        return self.terminal.platform.create_virtio_blk_device(self.volume_id, 0)

    def _assertion_after_step(self):
        assert self.vm.get_number_of_virtio_blk_devices() == 1

    def run(self):
        self._assertions_before_step()
        device_handle = self._step()
        self._assertion_after_step()
        return device_handle


class DeleteVirtioBlkStep(TestStep):
    def __init__(self, terminal, device_handle, vm, is_teardown=False):
        super().__init__(terminal, is_teardown)
        self.device_handle = device_handle
        self.vm = vm

    def _assertions_before_step(self):
        assert self.vm.get_number_of_virtio_blk_devices() == 1
        # todo check if vm is running properly

    def _step(self):
        self.terminal.platform.delete_virtio_blk_device(self.device_handle)

    def _assertion_after_step(self):
        assert self.vm.get_number_of_virtio_blk_devices() == 0
