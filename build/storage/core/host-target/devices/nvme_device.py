# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#
import logging
from typing import Callable

from pci import PciAddress

from devices import StoragePcieDevice, DeviceError
from drivers import DeviceDriver, SriovDeviceDriver


class NvmeDevice(StoragePcieDevice):
    def __init__(
        self,
        pci_addr: PciAddress,
        driver: DeviceDriver,
        volume_detector: Callable,
        fio_runner: Callable,
    ) -> None:
        super().__init__(pci_addr, driver, volume_detector, fio_runner)


class NvmePfDevice(NvmeDevice):
    def __init__(
        self,
        pci_addr: PciAddress,
        sriov_device_driver: SriovDeviceDriver,
        volume_detector: Callable,
        fio_runner: Callable,
    ) -> None:
        super().__init__(pci_addr, sriov_device_driver, volume_detector, fio_runner)
        self._sriov_driver = sriov_device_driver

    def plug(self) -> None:
        super().plug()
        logging.info(f"Pf {self._pci_addr} is bound to driver")
        if self._sriov_driver.is_sriov_supported(
            self._pci_addr
        ) and not self._sriov_driver.is_sriov_enabled(self._pci_addr):
            logging.info(f"Pf {self._pci_addr} enabling SRIOV")
            self._sriov_driver.enable_sriov(self._pci_addr)
            logging.info(f"Pf {self._pci_addr} SRIOV enabled")

    def unplug(self) -> None:
        if self._sriov_driver.are_vfs_enabled(self._pci_addr):
            raise DeviceError(f"Cannot delete pf {self._pci_addr} with bound vfs")

        if self._sriov_driver.is_sriov_supported(
            self._pci_addr
        ) and self._sriov_driver.is_sriov_enabled(self._pci_addr):
            logging.info(f"Pf {self._pci_addr} disabling SRIOV")
            self._sriov_driver.disable_sriov(self._pci_addr)
            logging.info(f"Pf {self._pci_addr} SRIOV disabled")
        super().unplug()

    def is_plugged(self) -> bool:
        if not super().is_plugged():
            return False
        if self._sriov_driver.is_sriov_supported(
            self._pci_addr
        ) and not self._sriov_driver.is_sriov_enabled(self._pci_addr):
            return False
        return True


class NvmeVfDevice(NvmeDevice):
    def __init__(
        self,
        pci_addr: PciAddress,
        driver: DeviceDriver,
        volume_detector: Callable,
        fio_runner: Callable,
    ) -> None:
        super().__init__(pci_addr, driver, volume_detector, fio_runner)
