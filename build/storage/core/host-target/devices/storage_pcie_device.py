# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#
import copy

from typing import Callable

from pci import PciAddress
from helpers.fio_args import FioArgs
from volumes import VolumeId

from drivers import DeviceDriver


class DeviceError(RuntimeError):
    pass


class StoragePcieDevice:
    def __init__(
        self,
        pci_addr: PciAddress,
        driver: DeviceDriver,
        volume_detector: Callable,
        fio_runner: Callable,
    ) -> None:
        self._pci_addr = pci_addr
        self._driver = driver
        self._find_volumes = volume_detector
        self._fio_runner = fio_runner

    def run_fio_on_volumes(self, fio_args: FioArgs, volume_ids: set[VolumeId]) -> str:
        volumes = self._find_volumes(self._pci_addr, volume_ids)
        volumes_as_strings = set(map(lambda x: str(x), volumes))
        fio_args = copy.deepcopy(fio_args)
        fio_args.add_volumes_to_exercise(volumes_as_strings)
        return self._fio_runner(fio_args)

    def is_plugged(self) -> bool:
        return self._driver.is_bound(self._pci_addr)

    def plug(self) -> None:
        if not self._driver.is_bound(self._pci_addr):
            self._driver.bind(self._pci_addr)

    def unplug(self) -> None:
        if self._driver.is_bound(self._pci_addr):
            self._driver.unbind(self._pci_addr)
