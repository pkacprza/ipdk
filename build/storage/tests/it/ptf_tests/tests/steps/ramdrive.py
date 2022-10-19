# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#

from tests.steps.base import TestStep


class CreateRamdriveAndAttachAsNsToSubsystemStep(TestStep):
    def _step(self):
        self.ramdrive_id = self.terminal.platform.create_ramdrive("Malloc0")

    def _assertion_after_step(self):
        assert self.ramdrive_id

    def run(self):
        self._step()
        self._assertion_after_step()
        return self.ramdrive_id


class CreateRamdriveAndAttachAsNsToSubsystem64Step(TestStep):
    def _step(self):
        volume_ids = []
        for i in range(64):
            ramdrive_id = self.terminal.platform.create_ramdrive(f"Malloc{i}")
            volume_ids.append(ramdrive_id)
        self.volume_ids = volume_ids

    def run(self):
        self._step()
        self._assertion_after_step()
        return self.volume_ids

    def _assertion_after_step(self):
        assert len(self.volume_ids) == 64


class CreateRamdriveAndAttachAsNsToSubsystemAbove64Step(TestStep):
    def _step(self):
        volume_ids = []
        for i in range(65):
            ramdrive_id = self.terminal.platform.create_ramdrive(f"Malloc{i}")
            volume_ids.append(ramdrive_id)
        self.volume_ids = volume_ids

    def _assertion_after_step(self):
        assert len(self.volume_ids) > 64

    def run(self):
        self._step()
        self._assertion_after_step()
        return self.volume_ids
