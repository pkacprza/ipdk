# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#

from tests.steps.base import TestStep


class CreateRamdriveAndAttachAsNsToSubsystemStep(TestStep):
    def _step(self):
        self.result["ramdrive_id"] = self.platform.create_ramdrive("Malloc0")

    def _assertion_after_step(self):
        assert self.result["ramdrive_id"]


class CreateRamdriveAndAttachAsNsToSubsystem64Step(TestStep):
    def _step(self):
        volume_ids = []
        for i in range(64):
            ramdrive_id = self.platform.create_ramdrive(f"Malloc{i}")
            volume_ids.append(ramdrive_id)
        self.result["volume_ids"] = volume_ids

    def _assertion_after_step(self):
        assert len(self.result["volume_ids"]) == 64


class CreateRamdriveAndAttachAsNsToSubsystemAbove64Step(TestStep):
    def _step(self):
        volume_ids = []
        for i in range(65):
            ramdrive_id = self.platform.create_ramdrive(f"Malloc{i}")
            volume_ids.append(ramdrive_id)
        self.result["volume_ids"] = volume_ids

    def _assertion_after_step(self):
        assert len(self.result["volume_ids"]) > 64
