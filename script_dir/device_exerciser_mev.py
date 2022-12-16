# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#

import os
import glob
import logging
from pci import PciAddress
from sma_handle import SmaHandle, SmaHandleError
from device_exerciser_if import DeviceExerciserError
from device_exerciser import *
from helpers.file_helpers import read_file


def make_device_exerciser() -> DeviceExerciserIf:
    return DeviceExerciserMev()


class MevSmaHandle(SmaHandle):
    def __init__(self, sma_handle) -> None:
        if not sma_handle:
            raise SmaHandleError("SMA handle cannot be empty")
        self._virtual_id = self._get_virtual_id(sma_handle)

    @staticmethod
    def _get_virtual_id(sma_handle):
        return int(sma_handle[sma_handle.rfind(".") + 1 :])

    def _find_mev_pf_pci_to_bind_driver(self):
        pci_devices = glob.glob("/sys/bus/pci/devices/*")
        for storage_pcie_device in pci_devices:
            pci_device_file = os.path.join(storage_pcie_device, "device")
            pci_device_vendor_file = os.path.join(storage_pcie_device, "vendor")
            pci_device_physfn = os.path.join(storage_pcie_device, "physfn")
            if (
                os.path.exists(pci_device_file)
                and read_file(pci_device_file).strip() == "0x1457"
                and os.path.exists(pci_device_vendor_file)
                and read_file(pci_device_vendor_file).strip() == "0x8086"
                and not os.path.exists(pci_device_physfn)
            ):
                logging.info(f"MEV pf is {storage_pcie_device}")
                return self._get_pci_addr_from_path(
                    os.path.basename(storage_pcie_device)
                )
        raise DeviceExerciserError("Cannot find MEV pf.")

    def _get_pci_addr_from_path(self, device_path):
        path_with_pci_addr = os.path.realpath(device_path)
        return PciAddress(os.path.basename(path_with_pci_addr))

    def is_virtual(self):
        if self._virtual_id == 0:
            return False
        return True

    def get_pci_address(self):
        pf_pci_addr = self._find_mev_pf_pci_to_bind_driver()
        if not self.is_virtual():
            logging.info(f"Pf pci address is {pf_pci_addr}")
            return pf_pci_addr
        else:
            pf_path = f"/sys/bus/pci/devices/{pf_pci_addr}"
            return self._get_pci_addr_from_path(
                os.path.join(pf_path, f"virtfn{int(self._virtual_id) - 1}")
            )

    def get_protocol(self):
        return "nvme"


class DeviceExerciserMev(DeviceExerciser):
    def _create_sma_handle(self, device_handle: str) -> SmaHandle:
        return MevSmaHandle(device_handle)