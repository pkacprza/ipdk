# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#

from tenacity import retry, stop_after_delay
from tests.steps.base import TestStep


class CreateAndExposeSubsystemOverTCPStep(TestStep):
    @retry(stop=stop_after_delay(120), reraise=True)
    def _assertions_before_step(self):
        out = self.terminal.execute("sudo netstat -anop | grep '4420 ' || true")
        if out:
            raise Exception("Port 4420 is not free")

    def _step(self):
        self.terminal.platform.create_subsystem()

    def _assertion_after_step(self):
        out = self.terminal.execute("sudo netstat -anop | grep '4420 '")
        assert "spdk_tgt" in out
