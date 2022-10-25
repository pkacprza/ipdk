# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#

import os
from abc import ABC, abstractmethod

from dotenv import load_dotenv

from system_tools.const import STORAGE_DIR_PATH


class BaseConfig(ABC):
    load_dotenv()

    @abstractmethod
    def __init__(self):
        pass

    def _getenv(self, env_name, alternative=None):
        env = os.getenv(env_name)
        return env if env else alternative


class BasePlatformConfig(BaseConfig):
    def __init__(self, platform_name):
        self.username = os.getenv("_".join([platform_name, "USERNAME"]))
        self.password = os.getenv("_".join([platform_name, "PASSWORD"]))
        self.ip_address = os.getenv("_".join([platform_name, "IP_ADDRESS"]))
        self.port = os.getenv("_".join([platform_name, "PORT"]))
        self.workdir = os.getenv(
            "_".join([platform_name, "WORKDIR"]),
            f"/home/{self.username}/ipdk_tests_workdir",
        )

    @property
    def storage_dir(self):
        return os.path.join(self.workdir, STORAGE_DIR_PATH)


class MainPlatformConfig(BasePlatformConfig):
    def __init__(self, platform_name):
        username = os.getenv("_".join([platform_name, "USERNAME"]))
        super().__init__(platform_name) if username else super().__init__(
            "MAIN_PLATFORM"
        )


class StorageTargetConfig(MainPlatformConfig):
    def __init__(self):
        super().__init__("STORAGE_TARGET")


class IPUStorageConfig(MainPlatformConfig):
    def __init__(self):
        super().__init__("IPU_STORAGE")


class HostTargetConfig(MainPlatformConfig):
    def __init__(self):
        super().__init__("HOST_TARGET")
        share_dir_path = self._getenv("SHARE_DIR_PATH", "shared")
        self.vm_share_dir_path = os.path.join(self.workdir, share_dir_path)
